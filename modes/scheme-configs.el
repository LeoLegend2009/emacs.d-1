;; Scheme
(setq scheme-program-name "gsi -:d-")
(setq gambit-unhighlight-after-command t)

(autoload 'gambit-inferior-mode "gambit" "Hook Gambit mode into cmuscheme.")
(autoload 'gambit-mode "gambit" "Hook Gambit mode into scheme.")

(add-hook 'inferior-scheme-mode-hook (function gambit-inferior-mode))
(add-hook 'scheme-mode-hook (function gambit-mode))
(add-hook 'scheme-mode-hook (function highlight-parentheses-mode))
(add-hook 'scheme-mode-hook 'light-symbol-mode)
(add-hook 'scheme-mode-hook 'paredit-mode)


;; (put 'dbind 'scheme-indent-function 2)
;; (put 'with-gensyms 'scheme-indent-function 1)
;; (put 'add-method 'scheme-indent-function 1)
;; (put 'make-method 'scheme-indent-function 1)
;; (put 'rember* 'scheme-indent-function 1)
;; (put 'match 'scheme-indent-function 1)
;; (put 'let1 'scheme-indent-function 2)
;; (put 'with 'scheme-indent-function 4)
;; (put 'mac 'scheme-indent-function 2)
;; (put 'def 'scheme-indent-function 2)

;; (font-lock-add-keywords 'scheme-mode '(("\\({\\|}\\)" 1 quack-pltish-module-defn-face)
;; 				       ("(\\(def\\(class\\|method\\)\\)" 1 quack-pltish-keyword-face)
;; 				       ("(\\(\\(\\(.*?#\\)\\|\\(c-\\)\\)?define\\(-[^ ]+ \\)?\\)" 1 quack-pltish-keyword-face)
;; 				       ("(define\\(-[^ ]+\\)? +(? *\\(\\w[^ ]+\\))" 2 quack-pltish-defn-face)
;; 				       ("(c-define +(? *\\(\\w[^ ]+\\)" 2 quack-pltish-defn-face)
;; 				       ;; ("\\(let1\\)" 1 quack-pltish-keyword-face)
;; 				       ("\\s \\(\\w\\S *?:\\)\\s " 1 quack-pltish-class-defn-face)
;; 				       p(".*;+.*`\\(.+?\\)'" 1 quack-pltish-selfeval-face)))