  function openDeleteModal(id) {
    document.getElementById('deleteParticipantId').value = id;
    new bootstrap.Modal(document.getElementById('deleteParticipantModal')).show();
  }

  function openProfileModal(participantId) {
    fetch(`/api/participants/${participantId}/profile/`)
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('participantProfileContent');
        container.innerHTML = `
          <p><strong>Имя:</strong> ${data.full_name}</p>
          <p><strong>Логин:</strong> ${data.username}</p>
          <p><strong>Email:</strong> ${data.email}</p>
          <p><strong>Должность:</strong> ${data.role_display}</p>
          <p><strong>Описание:</strong> ${data.bio || '—'}</p>
          <div>
            <strong>Фото:</strong><br>
            ${data.photo_url ? `<img src="${data.photo_url}" class="img-fluid rounded" style="max-height: 200px;">` : 'Фото нет'}
          </div>
        `;
        new bootstrap.Modal(document.getElementById('participantProfileModal')).show();
      });
  }