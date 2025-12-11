(function(){
  document.addEventListener('DOMContentLoaded', function(){
    var dropzone = document.getElementById('dropzone');
    var fileInput = document.getElementById('id_file_obj'); // Исправлено имя
    
    if(dropzone && fileInput) {
      // Обработчики для drag & drop
      ['dragenter','dragover'].forEach(function(eventName){
        dropzone.addEventListener(eventName, function(e){
          e.preventDefault();
          dropzone.classList.add('dragover');
        });
      });
      
      ['dragleave','drop'].forEach(function(eventName){
        dropzone.addEventListener(eventName, function(e){
          e.preventDefault();
          dropzone.classList.remove('dragover');
        });
      });
      
      dropzone.addEventListener('drop', function(e){
        var files = e.dataTransfer.files;
        if(files && files.length > 0) {
          // Обновляем input файлом
          fileInput.files = files;
          
          // Показываем имя файла
          var fileName = files[0].name;
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
      });
      
      // Обработчик клика на dropzone
      dropzone.addEventListener('click', function(e){
        if(e.target === dropzone || e.target.closest('.dropzone-inner')) {
          fileInput.click();
        }
      });
      
      // Обработчик изменения input
      fileInput.addEventListener('change', function(e){
        if(fileInput.files && fileInput.files.length > 0) {
          var fileName = fileInput.files[0].name;
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
      });
    }
  });
})();

function copyToken(e){
  e.preventDefault();
  var token = e.currentTarget.getAttribute('data-token');
  if(!token) return;
  
  // Пытаемся скопировать в буфер обмена
  navigator.clipboard.writeText(token).then(function(){
    // Успешно скопировано
    var btn = e.currentTarget;
    var originalText = btn.textContent;
    btn.textContent = 'Скопировано!';
    btn.style.backgroundColor = '#0a0';
    btn.style.color = '#fff';
    
    setTimeout(function(){
      btn.textContent = originalText;
      btn.style.backgroundColor = '';
      btn.style.color = '';
    }, 2000);
    
  }).catch(function(err){
    // Fallback для старых браузеров
    var tempInput = document.createElement('input');
    tempInput.value = token;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    
    var btn = e.currentTarget;
    var originalText = btn.textContent;
    btn.textContent = 'Скопировано';
    
    setTimeout(function(){
      btn.textContent = originalText;
    }, 2000);
  });
}