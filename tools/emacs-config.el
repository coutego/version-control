;; -*- lexical-binding: t; -*-
;; Specific emacs configuration and utilities for this project

(defconst ctg-vc-project-root (f-parent (f-parent (or load-file-name buffer-file-name))))
(setenv "CTG_VC_PROJECT_ROOT" ctg-vc-project-root)

(defun ctg-vc-debug (args)
  "Start the debugger with an appropriate configuration"
  (interactive "MPass options to program: vc ")
  (realgud:pdb (concat ctg-vc-project-root "/tools/debug.sh " args)))

(provide 'ctg-vc-config)
;;; emacs-config.el ends here
