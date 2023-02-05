function ajax(url, method, successCallback) {
	var xhr = new XMLHttpRequest();
	xhr.open(method, url);
	xhr.onreadystatechange = function() {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			successCallback(xhr.responseText);
		}
	};
	xhr.send();
}