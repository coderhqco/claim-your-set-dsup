    // submit the generate key on laod for the first time.
    let generate_key = document.getElementById('send_generate_key')
    if (generate_key !==null){
      let form = generate_key.closest('form')
      form.submit()
    }

    // copy the invitation key
    let invitation_key = document.getElementById('copy_invitation_key');
    invitation_key.addEventListener('click', function(event){
      let key = event.target.previousSibling.previousSibling.innerText;
       /* Copy the text inside the text field */
       copyToClipboard(key)
          .then(() => document.getElementById('copied').innerHTML = 'copied!')
          .catch(() => alert('make sure you are using https'));

        })
  
        // return a promise
        function copyToClipboard(textToCopy) {
            // navigator clipboard api needs a secure context (https)
            if (navigator.clipboard && window.isSecureContext) {
                // navigator clipboard api method'
                return navigator.clipboard.writeText(textToCopy);
            } else {
                // text area method
                let textArea = document.createElement("textarea");
                textArea.value = textToCopy;
                // make the textarea out of viewport
                textArea.style.position = "fixed";
                textArea.style.left = "-999999px";
                textArea.style.top = "-999999px";
                textArea.style.opacity = 0;
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                return new Promise((res, rej) => {
                    // here the magic happens
                    document.execCommand('copy') ? res() : rej();
                    textArea.remove();
                });
            }
        }