# Primary credit for the global-Hadamard SWAP identity

Sergey Bravyi and Dmitri Maslov, *Hadamard-free circuits expose the structure of the Clifford group*, IEEE Transactions on Information Theory67(7),4546–4563(2021), DOI[10.1109/TIT.2021.3081415](https://doi.org/10.1109/TIT.2021.3081415), [arXiv2003.09412v2](https://arxiv.org/abs/2003.09412v2), revised2021-07-07, give the exact normalized identity in equation(34), PDFpage21:

`SWAP*CZ = H^{tensor2}*CZ*H^{tensor2}*CZ*H^{tensor2}`.

Multiplying by`CZ` and using its commutation with`SWAP` gives `(CZ*H^{tensor2})^3=SWAP`. The campaign's Gaussian-dyadic convention`H0=H/sqrt(2)` therefore changes the two-wire cube by the scalar`1/8`; that scalar conversion is a direct derivation, not a new Clifford gate identity. These citations supply algebraic credit rather than fixed-tape movement, recursive costs or compiler premises.

An earlier primary construction is Joseph Fitzsimons and Jason Twamley, [*Globally controlled quantum wires for perfect qubit transport, mirroring and computing*](https://arxiv.org/abs/quant-ph/0601120), submitted2006-01-18. Figure2 and the page2 argument use a global Hadamard/CZ clock to mirror an entire chain after`N+1` applications. Its two-site specialization is related to the same normalized SWAP algebra. The campaign retains its own exact scalar and arbitrary-input controls.

Both primary papers were inspected via their arXiv PDFs at2026-10-08 17:45 UTC. No new RaD campaign source was used for this literature credit.
