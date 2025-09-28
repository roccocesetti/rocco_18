console.log("disconnect_confirm");

odoo.define('disconnect_confirm', function (require) {
    "use strict";

    const ajax = require('web.ajax');

    function waitForElement(selector, callback, maxAttempts = 50, interval = 300) {
        let attempts = 0;
        const timer = setInterval(() => {
            const $el = $(selector);
            if ($el.length > 0) {
                clearInterval(timer);
                callback($el);
            } else if (++attempts >= maxAttempts) {
                clearInterval(timer);
                console.warn(`Element not found: ${selector}`);
            }
        }, interval);
    }

    waitForElement('#disconnect_button', function ($btn) {
        console.log("Disconnect button found and bound");

        $btn.on('click', function () {
            if (confirm("Are you sure you want to disconnect the platform?")) {
                ajax.jsonRpc('/web/dataset/call_kw/res.config.settings/disconnect_platform', 'call', {
                    args: [],
                    kwargs: {}
                }).then(function (result) {
                    if (result && result.success) {
                        alert("Disconnected successfully.");
                        location.reload();
                    } else {
                        const error = result?.error || "Unknown error";
                        alert("Failed to disconnect: " + error);
                    }
                }).catch(function (err) {
                    alert("RPC error: " + err.message);
                });
            } else {
                console.log("User cancelled");
            }
        });
    });
});
