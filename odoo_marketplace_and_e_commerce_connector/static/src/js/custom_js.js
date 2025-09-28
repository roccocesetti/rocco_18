odoo.define('custom_js', function (require) {
    "use strict";

    const domReady = require('web.dom_ready');
    const notification = require('web.notification');

    domReady(() => {
        console.log("Custom JS Loaded");

        document.querySelectorAll('.copy-btn').forEach(button => {
            button.addEventListener('click', function (event) {
                event.preventDefault();
                console.log("Copy button clicked");

                const copyId = this.getAttribute('data-copy-id');
                const element = document.getElementById(copyId);

                if (element) {
                    const textToCopy = element.textContent.trim();
                    console.log("Text to copy:", textToCopy);

                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(textToCopy).then(() => {
                            new notification.Notification(this, {
                                title: "Copied",
                                message: `Copied: ${textToCopy}`,
                                type: 'success',
                            }).show();
                        }).catch(err => {
                            console.error("Clipboard API failed", err);
                            alert("Copy failed");
                        });
                    } else {
                        alert("Clipboard API not supported in your browser.");
                    }
                } else {
                    alert("Copy source element not found.");
                }
            });
        });
    });
});
