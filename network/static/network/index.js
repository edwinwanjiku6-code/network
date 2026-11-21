function getCookie(name) {const cookie = document.cookie;
    const cookieArray = cookie.split(';');
    const result = cookieArray.find(cookie => cookie.trim().startsWith(name + '='))
return result.split('=')[1];
}
document.addEventListener('DOMContentLoaded', function() {
    const posts = document.querySelectorAll('.post');
    posts.forEach(post => {
        const likeButton = post.querySelector('.like-button');
        likeButton.addEventListener('click', (event) => {event.preventDefault();
            fetch(`/like/${post.id}`, {method: 'POST', headers: {'X-CSRFToken': getCookie('csrftoken')}})
            .then(response => response.json())
            .then(data =>{if (data.liked === true) {likeButton.textContent = 'unlike'} else {likeButton.textContent = 'like'} 
         likeCount.textContent = `${data.like_count} likes`})
        })
        const likeCount = post.querySelector('.like-count');
        const actions = post.querySelector('.post-actions');
        const comment = document.createElement('button');
        comment.type = 'button'
        const form = post.querySelector('.comment-form')
        comment.addEventListener('click', () => {
            if (form.style.display === 'none'){
            form.style.display = 'block';}
            else {form.style.display = 'none'};
            
        })
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            const content = form.querySelector('textarea').value;
            if (content.trim() !== ""){
                fetch(`/comment/${post.id}`, 
                    {method: 'POST', 
                    headers: {'X-CSRFToken': getCookie('csrftoken')}, 
                    body: new FormData(form)})
                    .then(response => response.json())
                    .then(data => {
                
                    form.style.display = 'none';
                    form.reset();
                    
                    }) 
            }
        })
        comment.textContent = 'Comment';
        actions.appendChild(comment);
        const button = document.createElement('button');
        button.textContent = 'Edit-post';
        actions.appendChild(button);
        button.addEventListener('click', function() {
            const content = post.querySelector('.post-content');
            const existingText = content.textContent;
            const textarea = document.createElement('textarea');
            textarea.value = existingText;
            post.replaceChild(textarea, content);

            const saveButton = document.createElement('button');
            saveButton.textContent = 'Save';
            post.appendChild(saveButton);
            saveButton.addEventListener('click', function() {
            const textarea = post.querySelector('textarea');
            const newText = textarea.value;
            fetch(`/edit_post/${post.id}`, {method: "PUT", body: JSON.stringify({content: newText})}, )
            content.textContent = newText;
            post.replaceChild(content, textarea);
            post.removeChild(saveButton);
        });

        });
    });
});