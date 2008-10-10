(defun haskell-unicode ()
  (interactive)
  (substitute-patterns-with-unicode
   (list (cons "\\(<-\\)" 'left-arrow)
	 (cons "\\(->\\)" 'right-arrow)
	 (cons "[^=]\\(==\\)[^>=]" 'identical)
	 (cons "\\(/=\\)" 'not-identical)
	 ;; (cons "\\(\\[\\]\\)" 'nil)
	 (cons "\\<\\(sqrt\\)\\>" 'square-root)
	 ;; (cons "[^&]\\(&&\\)[^&]" 'logical-and)
	 ;; (cons "\\(||\\)" 'logical-or)
	 (cons " \\<\\(not\\)\\> " 'logical-neg)
	 (cons "[^>]\\(>\\)\\[^>=\\]" 'greater-than)
	 (cons "\\(<\\)\\[^=\\]" 'less-than)
	 (cons "[^>]\\(>=\\)" 'greater-than-or-equal-to)
	 (cons "\\(<=\\)" 'less-than-or-equal-to)
	 (cons " \\<\\(alpha\\)\\> " 'alpha)
	 (cons " \\<\\(beta\\)\\> " 'beta)
	 (cons " \\<\\(gamma\\)\\> " 'gamma)
	 (cons " \\<\\(delta\\)\\> " 'delta)
         (cons " \\<\\(Delta\\)\\> " 'Delta)
	 (cons "[ (]\\(\\\\\\)" 'lambda)
	 ;; (cons "\\(''\\) " 'double-prime)
	 ;; (cons "\\('\\) [^p']" 'prime)
	 (cons "\\(!!\\)" 'double-exclamation)
	 (cons "\\(forall\\)" 'for-all)
	 (cons "\\(\\.\\.\\)" 'horizontal-ellipsis))))

(add-hook 'haskell-mode-hook 'haskell-indent-mode)
(add-hook 'haskell-mode-hook 'haskell-doc-mode)
(add-hook 'haskell-mode-hook 'haskell-unicode)
(add-hook 'haskell-ghci-hook 'haskell-unicode)
(add-hook 'haskell-ghci-hook 'haskell-indent-mode)
(add-hook 'haskell-ghci-hook 'haskell-doc-mode)
(add-hook 'haskell-mode-hook 'turn-on-haskell-ghci)
(add-hook 'haskell-mode-hook 'turn-on-haskell-font-lock)
