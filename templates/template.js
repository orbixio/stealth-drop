var base64Data = "{encoded_data}";

var binaryString = window.atob(base64Data);
var len = binaryString.length;
var bytes = new Uint8Array(len);
for (var i = 0; i < len; i++) {
  bytes[i] = binaryString.charCodeAt(i);
}

var myBlob = new Blob([bytes], { type: "application/octet-stream" });
var myUrl = window.URL.createObjectURL(myBlob);
var randomDelay = Math.floor(Math.random() * 5000);

var myAnchor = document.createElement("a");
myAnchor.href = myUrl;
myAnchor.download = "{filename}";
setTimeout(function () {
  myAnchor.click();
}, randomDelay);
