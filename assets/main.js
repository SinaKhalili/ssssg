var parser = new DOMParser();

function goToPostOnPage(path) {
    let elem = document.getElementById(path);
    elem.classList.add('pulse-animation');
    elem.scrollIntoView({behavior: "smooth", block: "start", inline: "start"});
    setTimeout(function(){
        elem.classList.remove('pulse-animation');
    }, 1500);
}

function getPage(path) {
    let root = document.getElementById('root');
    if (root === null) {
        window.location.href = path;
    } else if (document.getElementById(path) != null) {
        goToPostOnPage(path)
    } else {
        fetch(path)
          .then(response => response.text())
          .then(data => {
            let htmlDoc = parser.parseFromString(data, 'text/html');
            let body = htmlDoc.getElementById('content');
            let body_str = body.innerHTML;

            let root = document.getElementById('root');
            root.insertAdjacentHTML('afterend', body_str);
            
            goToPostOnPage(path)
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