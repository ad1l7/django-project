function openProfileModal(participantId) {
  fetch(getProfileUrl(participantId))
    .then(response => {
      if (!response.ok) throw new Error('Ошибка при получении профиля');
      return response.json();
    })
    .then(data => {
      document.getElementById('profile-name').textContent = data.full_name;
      document.getElementById('profile-username').textContent = data.username;
      document.getElementById('profile-email').textContent = data.email;
      document.getElementById('profile-position').textContent = data.position;
      document.getElementById('profile-bio').textContent = data.bio || 'Нет описания';
      const photo = document.getElementById('profile-photo');

      if (data.photo_url) {
        photo.src = data.photo_url;
        photo.alt = 'Фото профиля';
      } else {
        photo.src = '';
        photo.alt = 'Фото отсутствует';
      }

      const modal = new bootstrap.Modal(document.getElementById('profileModal'));
      modal.show();
    })
    .catch(error => console.error('Ошибка:', error));
}


function openDeleteModal(participantId) {
  const input = document.getElementById('deleteParticipantId');
  if (input) {
    input.value = participantId;
    const modal = new bootstrap.Modal(document.getElementById('deleteParticipantModal'));
    modal.show();
  }
}

