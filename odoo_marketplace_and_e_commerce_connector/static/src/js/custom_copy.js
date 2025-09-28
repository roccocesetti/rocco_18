odoo.define('custom_copy', function (require) {
    "use strict";

    const domReady = require('web.dom_ready');
    const Notification = require('web.notification');

    domReady(() => {
        document.querySelectorAll('.copy-btn').forEach(button => {
            button.addEventListener('click', function (event) {
                event.preventDefault();
                const copyId = this.getAttribute('data-copy-id');
                const element = document.getElementById(copyId);
                let textToCopy = "";

                if (element) {
                    const span = element.querySelector('span');
                    textToCopy = span ? span.innerText.trim() : element.innerText.trim();

                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(textToCopy).then(() => {
                            new Notification(this, {
                                title: "Copied",
                                message: `Copied: ${textToCopy}`,
                                type: 'success',
                            }).show();
                        }).catch(err => {
                            console.error("Clipboard error:", err);
                            alert("Copy failed");
                        });
                    } else {
                        alert("Clipboard API not supported.");
                    }
                } else {
                    alert("Element to copy not found.");
                }
            });
        });
    });
});
