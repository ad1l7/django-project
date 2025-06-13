
  document.addEventListener('DOMContentLoaded', function () {
    const messagesContainer = document.querySelector('.chat-messages');
    let lastMessageCount = 0;

    function fetchMessages() {
      fetch("{% url 'dashboard:fetch_project_messages' project.id %}")
        .then(response => response.json())
        .then(data => {
          if (data.messages.length === lastMessageCount) return; // нет новых сообщений

          // Обновляем только если появились новые
          lastMessageCount = data.messages.length;
          const wasAtBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop <= messagesContainer.clientHeight + 50;

          messagesContainer.innerHTML = ''; // очистка, но только при необходимости
          data.messages.forEach(msg => {
            const div = document.createElement('div');
            div.className = `message ${msg.is_user ? 'message-sent' : 'message-received'}`;
            let attachmentHTML = '';
            if (msg.attachment_url) {
              attachmentHTML = `
                <div class="message-text">
                  📎 <a href="${msg.attachment_url}" target="_blank" download>
                    Скачать файл
                  </a>
                </div>`;
            }
            
            div.innerHTML = `
              <div class="message-sender">${msg.sender} ${msg.is_user ? '(Вы)' : ''}</div>
              ${msg.content ? `<div class="message-text">${msg.content}</div>` : ''}
              ${attachmentHTML}
              <div class="message-time">${msg.timestamp}</div>
            `;

            messagesContainer.appendChild(div);
          });

          if (wasAtBottom) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
          }
        });
    }

    fetchMessages(); // первый запуск
    setInterval(fetchMessages, 1000); // каждые 1 секунда
  });

