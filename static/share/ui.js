(function(){
  document.addEventListener('DOMContentLoaded', function(){
    
    // ========== DRAG & DROP ФУНКЦИОНАЛ ==========
    var dropzone = document.getElementById('dropzone');
    var fileInput = document.getElementById('id_file_obj');
    
    if(dropzone && fileInput) {
      // Обработчики для drag & drop
      ['dragenter','dragover'].forEach(function(eventName){
        dropzone.addEventListener(eventName, function(e){
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.add('dragover');
        });
      });
      
      ['dragleave','drop'].forEach(function(eventName){
        dropzone.addEventListener(eventName, function(e){
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.remove('dragover');
        });
      });
      
      dropzone.addEventListener('drop', function(e){
        var files = e.dataTransfer.files;
        if(files && files.length > 0) {
          fileInput.files = files;
          updateDropzoneText(files[0].name);
        }
      });

      
      fileInput.addEventListener('change', function(e){
        if(fileInput.files && fileInput.files.length > 0) {
          updateDropzoneText(fileInput.files[0].name);
        }
      });
      
      function updateDropzoneText(fileName) {
        var dropzoneInner = dropzone.querySelector('.dropzone-inner');
        if(dropzoneInner) {
          var strong = dropzoneInner.querySelector('strong');
          var span = dropzoneInner.querySelector('.muted');
          if(strong && span) {
            strong.textContent = fileName;
            span.textContent = 'Нажмите или перетащите другой файл';
          }
        }
      }
    }
    
    // ========== КОПИРОВАНИЕ ССЫЛКИ ==========
    document.addEventListener('click', function(e) {
      // Для кнопок с data-download-url
      if(e.target.matches('button[data-download-url]') || 
         e.target.closest('button[data-download-url]')) {
        var button = e.target.matches('button[data-download-url]') ? 
                     e.target : e.target.closest('button[data-download-url]');
        var downloadUrl = button.getAttribute('data-download-url');
        
        e.preventDefault();
        
        if(!downloadUrl) {
          console.error('Нет ссылки для копирования');
          return;
        }
        
        navigator.clipboard.writeText(downloadUrl).then(function(){
          var originalText = button.textContent;
          button.textContent = 'Ссылка скопирована!';
          
          setTimeout(function(){
            button.textContent = originalText;
          }, 2000);
          
        }).catch(function(err){
          // Fallback для старых браузеров
          var tempInput = document.createElement('input');
          tempInput.value = downloadUrl;
          document.body.appendChild(tempInput);
          tempInput.select();
          document.execCommand('copy');
          document.body.removeChild(tempInput);
          
          var originalText = button.textContent;
          button.textContent = 'Скопировано';
          
          setTimeout(function(){
            button.textContent = originalText;
          }, 2000);
        });
      }
      
      // Для обратной совместимости с data-token
      if(e.target.matches('button[data-token]') || 
         e.target.closest('button[data-token]')) {
        var button = e.target.matches('button[data-token]') ? 
                     e.target : e.target.closest('button[data-token]');
        var token = button.getAttribute('data-token');
        
        e.preventDefault();
        
        // Генерируем полную ссылку для скачивания
        var baseUrl = window.location.origin;
        var downloadUrl = baseUrl + "/sshare/download/" + token + "/";
        
        navigator.clipboard.writeText(downloadUrl).then(function(){
          var originalText = button.textContent;
          button.textContent = 'Ссылка скопирована!';
          
          setTimeout(function(){
            button.textContent = originalText;
          }, 2000);
          
        }).catch(function(err){
          // Fallback для старых браузеров
          var tempInput = document.createElement('input');
          tempInput.value = downloadUrl;
          document.body.appendChild(tempInput);
          tempInput.select();
          document.execCommand('copy');
          document.body.removeChild(tempInput);
          
          var originalText = button.textContent;
          button.textContent = 'Скопировано';
          
          setTimeout(function(){
            button.textContent = originalText;
          }, 2000);
        });
      }
    });
    
    // ========== ПРОВЕРКА НЕАКТИВНЫХ ССЫЛОК И УДАЛЕННЫХ ФАЙЛОВ ==========
    document.addEventListener('click', function(e) {
      // Проверка ссылок на скачивание
      if(e.target.matches('a[href*="/download/"]') || 
         e.target.closest('a[href*="/download/"]')) {
        var link = e.target.matches('a[href*="/download/"]') ? 
                   e.target : e.target.closest('a[href*="/download/"]');
        
        if(link.classList.contains('disabled') || 
           link.getAttribute('aria-disabled') === 'true') {
          e.preventDefault();
          alert('Эта ссылка неактивна или истек её срок действия');
          return false;
        }
      }
      
      // Проверка ссылок на страницу файла (file_links)
      if(e.target.matches('a[href*="/file-links/"]') || 
         e.target.closest('a[href*="/file-links/"]')) {
        var link = e.target.matches('a[href*="/file-links/"]') ? 
                   e.target : e.target.closest('a[href*="/file-links/"]');
        
        // Проверяем, не ведет ли ссылка на удаленный файл
        var fileItem = link.closest('.file-item');
        if(fileItem) {
          var fileNameElement = fileItem.querySelector('.file-name s');
          if(fileNameElement) { // Если есть зачеркнутый текст - файл удален
            e.preventDefault();
            alert('Этот файл удален. Вы не можете создавать ссылки для удаленных файлов.');
            return false;
          }
        }
      }
    });
    
  });
})();

// Функция для onclick (старая версия)
function copyToken(e){
  if(e) e.preventDefault();
  var button = e.currentTarget;
  
  // Пытаемся получить готовую ссылку из data-download-url
  var downloadUrl = button.getAttribute('data-download-url');
  
  // Если нет готовой ссылки, но есть токен - генерируем
  if(!downloadUrl) {
    var token = button.getAttribute('data-token');
    if(!token) return;
    
    var baseUrl = window.location.origin;
    downloadUrl = baseUrl + "/sshare/download/" + token + "/";
  }
  
  navigator.clipboard.writeText(downloadUrl).then(function(){
    var originalText = button.textContent;
    button.textContent = 'Ссылка скопирована!';
    
    setTimeout(function(){
      button.textContent = originalText;
    }, 2000);
    
  }).catch(function(err){
    // Fallback
    var tempInput = document.createElement('input');
    tempInput.value = downloadUrl;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    
    var originalText = button.textContent;
    button.textContent = 'Скопировано';
    
    setTimeout(function(){
      button.textContent = originalText;
    }, 2000);
  });
}