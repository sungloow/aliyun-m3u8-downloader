// ==UserScript==
// @name         51CTO视频下载
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://*.51cto.com/*
// @require https://scriptcat.org/lib/637/1.3.3/ajaxHooker.js
// @require https://scriptcat.org/lib/532/1.0.2/ajax.js
// @run-at       document-start
// @grant GM_xmlhttpRequest
// ==/UserScript==

function postData(url, data) {
    return new Promise(function(resolve, reject) {
      GM_xmlhttpRequest({
        method: 'POST',
        url,
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        data: JSON.stringify(data),
        onload(xhr) {
          resolve(xhr.responseText);
        }
      });
    });
  }
  
  (function() {
      'use strict';
      ajaxHooker.hook(request => {
          if (request.url.includes('https://edu.51cto.com/center/player/play/vod-play-auth')) {
              request.response = res => {
                  console.log(res.responseText);
                  res.responseText;
                  postData('http://127.0.0.1:15000', res);
              };
          }
      });
  })();
  