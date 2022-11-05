;; -*- lexical-binding: t; -*-
;; Specific emacs configuration and utilities for this project

(defconst ctg-vc-project-root (f-parent (f-parent (or load-file-name buffer-file-name))))
(setenv "CTG_VC_PROJECT_ROOT" ctg-vc-project-root)

(defgroup ctg-vc nil
  "Edit commands for project CTG-VC"
  :group 'editing)

(defcustom ctg-vc-intellij-command
  "intellij-idea-ultimate"
  "command to launch IntelliJ"
  :group 'ctg-vc
  :type '(string))

(defun ctg-vc-debug (args)
  "Start the debugger with an appropriate configuration"
  (interactive "MPass options to program: vc ")
  (realgud:pdb (concat ctg-vc-project-root "/tools/debug.sh " args)))

(defun ctg-vc-open-in-intellij ()
  "Open the current buffer in IntelliJ"
  (interactive)
  (save-buffer)
  (message
   (concat ctg-vc-intellij-command
           " --line "
           (int-to-string (line-number-at-pos))
           " "
           (buffer-file-name))
   )
  (start-process-shell-command "IntelliJ"
                               "*IntelliJ*"
                               (concat ctg-vc-intellij-command
                                       " --line "
                                       (int-to-string (line-number-at-pos))
                                       " "
                                       (buffer-file-name))))

(provide 'ctg-vc-config)
;;; emacs-config.el ends here

