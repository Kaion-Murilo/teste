function atualizarPagina() {
    var currentPath = window.location.pathname;

    if (currentPath.startsWith('/leiamais/') && !sessionStorage.getItem('paginaAtualizada')) {
      sessionStorage.setItem('paginaAtualizada', true);
      location.reload();
    } else {
      sessionStorage.removeItem('paginaAtualizada');
    }
  }

  document.addEventListener('DOMContentLoaded', atualizarPagina);