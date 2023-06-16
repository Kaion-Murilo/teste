function toggleDados() {
    var dadosContainer = document.getElementById('dados-container');
    var cookiesEnabled = navigator.cookieEnabled;

    if (dadosContainer.style.display === 'none') {
      dadosContainer.style.display = 'block';

      if (cookiesEnabled) {
        setCookie('dadosVisiveis', 'true', 365);
      }
    } else {
      dadosContainer.style.display = 'none';

      if (cookiesEnabled) {
        setCookie('dadosVisiveis', 'false', 365);
      }
    }
  }

  function setCookie(name, value, days) {
    var expires = "";
    if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + expires + "; path=/";
  }

  function getCookie(name) {
    var nameEQ = name + "=";
    var cookies = document.cookie.split(';');

    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();

      if (cookie.indexOf(nameEQ) === 0) {
        return cookie.substring(nameEQ.length);
      }
    }

    return null;
  }

  function getLastVisitedPage() {
    var lastVisitedPage = getCookie('ultimaPagina');
    setCookie('ultimaPagina', window.location.pathname, 365);
    return lastVisitedPage;
  }

  window.addEventListener('load', function() {
    var cookiesEnabled = navigator.cookieEnabled;
    var lastVisitedPage = getLastVisitedPage();
    var dadosVisiveis = getCookie('dadosVisiveis');
    var dadosContainer = document.getElementById('dados-container');

    if (lastVisitedPage !== '/leiamais' || dadosVisiveis !== 'true') {
      dadosContainer.style.display = 'none';
      setCookie('dadosVisiveis', 'false', 365);
    } else {
      dadosContainer.style.display = 'block';
    }

    if (!cookiesEnabled) {
      alert('Os cookies estão desabilitados. O estado dos dados não será mantido após sair da página.');
    }
  });