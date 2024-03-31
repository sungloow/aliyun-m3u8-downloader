package download

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"os"
	"path"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"

	"github.com/ddliu/go-httpclient"

	"github.com/lbbniu/aliyun-m3u8-downloader/pkg/parse"
	"github.com/lbbniu/aliyun-m3u8-downloader/pkg/parse/aliyun"
	"github.com/lbbniu/aliyun-m3u8-downloader/pkg/tool"
)

const (
	tsFolderName     = "ts"
	tsTempFileSuffix = "_tmp"
	progressWidth    = 40
)

var (
	mergeTSFilename string
)

type Downloader struct {
	lock     sync.Mutex
	queue    []int
	folder   string
	tsFolder string
	finish   int32
	segLen   int

	result *parse.Result
}

// NewTask returns a Task instance
func NewTask(output string, url string, aliKey string) (*Downloader, error) {
	result, err := parse.FromURL(url, aliKey)
	// 从output中提取最后一部分作为mergeTSFilename
	parts := strings.Split(output, "/")
	mergeTSFilename = parts[len(parts)-1] + ".mp4"
	// 从output中删除提取出的部分
	output = strings.TrimSuffix(output, "/"+parts[len(parts)-1])

	// mergeTSFilename = tsFilename(url) + ".mp4"
	if err != nil {
		return nil, err
	}
	var folder string
	// If no output folder specified, use current directory
	if output == "" {
		current, err := tool.CurrentDir()
		if err != nil {
			return nil, err
		}
		folder = filepath.Join(current, output)
	} else {
		folder = output
	}
	if err := os.MkdirAll(folder, os.ModePerm); err != nil {
		return nil, fmt.Errorf("create storage folder failed: %s", err.Error())
	}
	tsFolder := filepath.Join(folder, tsFolderName)
	if err := os.MkdirAll(tsFolder, os.ModePerm); err != nil {
		return nil, fmt.Errorf("create ts folder '[%s]' failed: %s", tsFolder, err.Error())
	}
	d := &Downloader{
		folder:   folder,
		tsFolder: tsFolder,
		result:   result,
	}
	d.segLen = len(result.M3u8.Segments)
	d.queue = genSlice(d.segLen)
	return d, nil
}

// Start runs downloader
func (d *Downloader) Start(concurrency int) error {
	var wg sync.WaitGroup
	// struct{} zero size
	limitChan := make(chan struct{}, concurrency)
	for {
		tsIdx, end, err := d.next()
		if err != nil {
			if end {
				break
			}
			continue
		}
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			if err := d.download(idx); err != nil {
				// Back into the queue, retry request
				fmt.Printf("[failed] %s\n", err.Error())
				if err := d.back(idx); err != nil {
					fmt.Printf(err.Error())
				}
			}
			<-limitChan
		}(tsIdx)
		limitChan <- struct{}{}
	}
	wg.Wait()
	if err := d.mergeHsToMp4(); err != nil {
		return err
	}
	return nil
}

func (d *Downloader) download(segIndex int) error {
	tsUrl := d.tsURL(segIndex)
	resp, err := httpclient.Get(tsUrl)
	if err != nil {
		return fmt.Errorf("request %s, %s", tsUrl, err.Error())
	}
	filename := tsFilename(tsUrl)
	//noinspection GoUnhandledErrorResult
	fPath := filepath.Join(d.tsFolder, filename)
	fTemp := fPath + tsTempFileSuffix
	f, err := os.Create(fTemp)
	if err != nil {
		return fmt.Errorf("create file: %s, %s", filename, err.Error())
	}
	tsData, err := resp.ReadAll()
	if err != nil {
		return fmt.Errorf("read bytes: %s, %s", tsUrl, err.Error())
	}
	sf := d.result.M3u8.Segments[segIndex]
	if sf == nil {
		return fmt.Errorf("invalid segment index: %d", segIndex)
	}
	keyInfo, ok := d.result.M3u8.Keys[sf.KeyIndex]
	if ok && keyInfo.Key != "" {
		// 是否阿里云私有加密
		if keyInfo.AliyunVoDEncryption {
			tsParser := aliyun.NewTSParser(tsData, keyInfo.Key)
			tsData = tsParser.Decrypt()
		} else {
			tsData, err = tool.AES128Decrypt(tsData, []byte(keyInfo.Key), []byte(keyInfo.IV))
			if err != nil {
				return fmt.Errorf("decryt: %s, %s", tsUrl, err.Error())
			}
		}
	}

	// https://en.wikipedia.org/wiki/MPEG_transport_stream
	// Some TS files do not start with SyncByte 0x47, they can not be played after merging,
	// Need to remove the bytes before the SyncByte 0x47(71).
	syncByte := uint8(71) //0x47
	bLen := len(tsData)
	for j := 0; j < bLen; j++ {
		if tsData[j] == syncByte {
			tsData = tsData[j:]
			break
		}
	}
	w := bufio.NewWriter(f)
	if _, err := w.Write(tsData); err != nil {
		return fmt.Errorf("write to %s: %s", fTemp, err.Error())
	}
	// Release file resource to rename file
	_ = f.Close()
	if err = os.Rename(fTemp, fPath); err != nil {
		return err
	}
	// Maybe it will be safer in this way...
	atomic.AddInt32(&d.finish, 1)
	//tool.DrawProgressBar("Downloading", float32(d.finish)/float32(d.segLen), progressWidth)
	fmt.Printf("[download %6.2f%%] %s\n", float32(d.finish)/float32(d.segLen)*100, tsUrl)
	return nil
}

func (d *Downloader) next() (segIndex int, end bool, err error) {
	d.lock.Lock()
	defer d.lock.Unlock()
	if len(d.queue) == 0 {
		err = fmt.Errorf("queue empty")
		if d.finish == int32(d.segLen) {
			end = true
			return
		}
		// Some segment indexes are still running.
		end = false
		return
	}
	segIndex = d.queue[0]
	d.queue = d.queue[1:]
	return
}

func (d *Downloader) back(segIndex int) error {
	d.lock.Lock()
	defer d.lock.Unlock()
	if sf := d.result.M3u8.Segments[segIndex]; sf == nil {
		return fmt.Errorf("invalid segment index: %d", segIndex)
	}
	d.queue = append(d.queue, segIndex)
	return nil
}

func (d *Downloader) mergeHsToMp4() error {
	// In fact, the number of downloaded segments should be equal to number of m3u8 segments
	missingCount := 0
	for segIndex := 0; segIndex < d.segLen; segIndex++ {
		f := filepath.Join(d.tsFolder, tsFilename(d.tsURL(segIndex)))
		if _, err := os.Stat(f); err != nil {
			missingCount++
		}
	}
	if missingCount > 0 {
		fmt.Printf("[warning] %d files missing\n", missingCount)
	}

	// Create a TS file for merging, all segment files will be written to this file.
	mFilePath := filepath.Join(d.folder, mergeTSFilename)
	mFile, err := os.Create(mFilePath)
	if err != nil {
		return fmt.Errorf("create main TS file failed：%s", err.Error())
	}
	//noinspection GoUnhandledErrorResult
	defer mFile.Close()

	writer := bufio.NewWriter(mFile)
	mergedCount := 0
	for segIndex := 0; segIndex < d.segLen; segIndex++ {
		bytes, err := ioutil.ReadFile(filepath.Join(d.tsFolder, tsFilename(d.tsURL(segIndex))))
		_, err = writer.Write(bytes)
		if err != nil {
			continue
		}
		mergedCount++
		tool.DrawProgressBar("merge", float32(mergedCount)/float32(d.segLen), progressWidth)
	}
	_ = writer.Flush()
	// Remove `ts` folder
	_ = os.RemoveAll(d.tsFolder)

	if mergedCount != d.segLen {
		fmt.Printf("[warning] \n%d files merge failed", d.segLen-mergedCount)
	}

	fmt.Printf("\n[output] %s\n", mFilePath)

	return nil
}

func (d *Downloader) tsURL(segIndex int) string {
	seg := d.result.M3u8.Segments[segIndex]
	return tool.ResolveURL(d.result.URL, seg.URI)
}

func tsFilename(tsUrl string) string {
	idx := strings.Index(tsUrl, "?")
	if idx > 0 {
		return path.Base(tsUrl[:idx])
	}
	return path.Base(tsUrl)
}

func genSlice(len int) []int {
	s := make([]int, 0)
	for i := 0; i < len; i++ {
		s = append(s, i)
	}
	return s
}
