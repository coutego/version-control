((nil
  .
  ((eval
    .
    (unless (featurep 'ctg-vc-config)
      (defun ctg-vc--is-root-dir (d)
        (and (f-exists? (concat d "/.dir-locals.el"))
             (f-exists? (concat d "/tools/emacs-config.el"))))

      (let* ((start (or load-file-name buffer-file-name ""))
             (d (f-dirname start)))
        (unless (s-equals? "" start)
          (while (and (not (ctg-vc--is-root-dir d))
                      (not (s-equals? "../" d)))
            (setq d (f-parent d)))
          (if (not (s-equals? "../" d))
              (require 'ctg-vc-config (concat d "/tools/emacs-config.el"))))))))))
