var parser = new DOMParser();

function getPage(path) {
    let root = document.getElementById('root');
    if (root === null) {
        window.location.href = path;
    } else {
        fetch(path)
          .then(response => response.text())
          .then(data => {
            let htmlDoc = parser.parseFromString(data, 'text/html');
            let body = htmlDoc.getElementById('content');
            let body_str = body.innerHTML;

            let root = document.getElementById('root');
            root.insertAdjacentHTML('afterend', body_str);
            window.history.pushState({}, '', path);
        });
    }
}

function getPosts() {
    fetch("/")
      .then(response => response.text())
      .then(data => {
        let htmlDoc = parser.parseFromString(data, 'text/html');
        let body = htmlDoc.getElementById('posts');
        let body_str = body.innerHTML;
        body_str = '<div class="content-class">' + body_str + '</div>'

        let root = document.getElementById('root');
        root.insertAdjacentHTML('afterend', body_str);
    });
}

function getRandom() {
    console.log("get random");
}