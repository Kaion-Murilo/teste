function showMoreActors() {
    var rows = document.querySelectorAll('.film-info-card .row:not(:first-child)');
    for (var i = 0; i < rows.length; i++) {
      if (i < 5) {
        rows[i].style.display = 'flex';
      } else {
        rows[i].style.display = 'none';
      }
    }
    document.querySelector('.show-more-button').style.display = 'none';
  }
        function showLessActors() {
    var rows = document.querySelectorAll('.film-info-card .row:not(:first-child)');
    for (var i = 0; i < rows.length; i++) {
      rows[i].style.display = 'none';
    }
    document.querySelector('.show-more-button').style.display = 'block';
  }
  