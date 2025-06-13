  const tasks = document.querySelectorAll('.task');
        const columns = document.querySelectorAll('.column');

        let draggedTask = null;

        tasks.forEach(task => {
            task.addEventListener('dragstart', () => {
                draggedTask = task;
            });
        });

        columns.forEach(column => {
            column.addEventListener('dragover', e => e.preventDefault());
            column.addEventListener('drop', () => {
                if (draggedTask) {
                    column.appendChild(draggedTask);
                    const taskId = draggedTask.dataset.id;
                    const newStatus = column.dataset.status;

                    fetch("{% url 'dashboard:update_task_status' %}", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': '{{ csrf_token }}'
                        },
                        body: JSON.stringify({ task_id: taskId, status: newStatus })
                    });
                }
            });
        });

function deleteTask(taskId) {
    const taskElement = document.querySelector(`.task[data-id='${taskId}']`);
    if (!taskElement) return;

    fetch("{% url 'dashboard:delete_personal_task' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ task_id: taskId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && taskElement) {
            // Анимация исчезновения
            taskElement.style.opacity = '0';
            taskElement.style.transform = 'translateX(30px)';
            setTimeout(() => {
                taskElement.remove();
            }, 300); // должно совпадать с CSS transition
        }
    });
}
console.log('aksak')