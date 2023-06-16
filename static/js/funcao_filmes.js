function showMoreActors() {
    var rows = document.querySelectorAll('.film-info-card .row:not(:first-child)');
    for (var i = 0; i < rows.length; i++) {
      if (i < 5) {
        rows[i].style.display = 'flex';
      } else {
        rows[i].style.display = 'none';
      }
    }
    document.querySelector('.show-more-button .show-more').classList.add('hide');
    document.querySelector('.show-more-button .show-less').classList.remove('hide');
  }

  function showLessActors() {
    var rows = document.querySelectorAll('.film-info-card .row:not(:first-child)');
    for (var i = 0; i < rows.length; i++) {
      rows[i].style.display = 'none';
    }
    document.querySelector('.show-more-button .show-more').classList.remove('hide');
    document.querySelector('.show-more-button .show-less').classList.add('hide');
  }