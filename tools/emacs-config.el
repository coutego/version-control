;;; emacs-config --- Specific Emacs configuration for this project
;; -*- lexical-binding: t; -*-
;;; Commentary:
;; Specific Emacs configuration and utilities for this project
;;; Code:

(require 'realgud)
(require 'f)

(defconst ctg-vc-project-root (f-parent (f-parent (or load-file-name buffer-file-name))))
(setenv "CTG_VC_PROJECT_ROOT" ctg-vc-project-root)
(setenv "PYTHONPATH" (concat (getenv "PYTHONPATH") ":" ctg-vc-project-root))

(defgroup ctg-vc nil
  "Edit commands for project CTG-VC."
  :group 'editing)

(defcustom ctg-vc-intellij-command
  "intellij-idea-ultimate"
  "Command to launch IntelliJ."
  :group 'ctg-vc
  :type '(string))

(defcustom ctg-vc-terminal-command
  "gnome-terminal --"
  "Command to launch the system terminal, ready to accept arguments."
  :group 'ctg-vc
  :type '(string))

(defun ctg-vc-debug (args)
  "Start the debugger with an appropriate configuration and pass ARGS."
  (interactive "MPass options to program: vc ")
  (save-buffer)
  (realgud:pdb (concat ctg-vc-project-root "/tools/debug.sh " args)))

(defun ctg-vc-pudb (args)
  "Start pudb with an appropriate configuration and pass ARGS."
  (interactive "MPass options to program: vc ")
  (save-buffer)
  (start-process-shell-command "PUDB"
                               "*pudb*"
                               (concat ctg-vc-terminal-command
                                       " "
                                       "pudb -m vc "
                                       args)))

(defun ctg-vc-open-in-intellij ()
  "Open the current buffer in IntelliJ."
  (interactive)
  (save-buffer)
  (message "Opening IntelliJ")
  (start-process-shell-command "IntelliJ"
                               "*IntelliJ*"
                               (concat ctg-vc-intellij-command
                                       " --line "
                                       (int-to-string (line-number-at-pos))
                                       " "
                                       (buffer-file-name))))

(define-key python-mode-map (kbd "C-c D") 'ctg-vc-debug)
(define-key python-mode-map (kbd "C-c d") 'ctg-vc-pudb)
(define-key python-mode-map (kbd "C-c i") 'ctg-vc-open-in-intellij)

(provide 'ctg-vc-config)
;;; emacs-config.el ends here

