    const loginTab    = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginDiv    = document.getElementById('loginFormContainer');
    const regDiv      = document.getElementById('registerFormContainer');

    loginTab.addEventListener('click', () => {
      loginDiv.classList.remove('hidden');
      regDiv.classList.add('hidden');
      loginTab.classList.add('active');
      registerTab.classList.remove('active');
    });
    registerTab.addEventListener('click', () => {
      regDiv.classList.remove('hidden');
      loginDiv.classList.add('hidden');
      registerTab.classList.add('active');
      loginTab.classList.remove('active');
    });