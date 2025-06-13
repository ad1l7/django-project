    // Анимация для сообщений чата
    document.querySelectorAll('.message').forEach((message, index) => {
      message.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Эффект при наведении на карточки
    document.querySelectorAll('.detail-card').forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
      });
    });