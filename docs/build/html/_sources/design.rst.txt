Design
======

Definitions
-----------

- ***the service*** - the oldspeak web app itself
- ***user*** - an anonymous person
- ***server*** - a cloud server that runs *the service*
- ***http mainstream*** - the nginx instance running in a *server* and
  proxying *the service*
- ***member*** - someone who has access to *the service*
- ***document*** - a text source + its metadata, versioned and
  encrypted at rest in the server's filesystem
- ***owner*** - a *member* that owns one or more *documents*
- ***fingerprint*** - the GPG fingerprint of a *member* or *owner*
- ***invitation*** - when a *member* adds another *fingerprint* to the
  service
- ***public key*** - a PGP public key armored in text-mode
- ***metadoc*** - the metadata of a document file (contains
  information like: its *owner's* *fingerprint*, creation date etc.)
- ***essay*** - a document that is published publicly in a permanent
  url.
- ***sys-admin*** - a person who has access to both *the service*
  running in a *server*
- ***application logs*** - all logs coming from *the service*
- ***server logs*** - all logs coming from the *http mainstream
  server*
- ***public logs*** - an aggregated anachronic stream that splices up
  all *application logs*
- ***storage system*** - an internal subsystem of *the service* whose
   contents are encrypted at rest and can only be accessed by a
   *sys-admin*.
- ***known fingerprint*** - a *fingerprint* that is allowed to join or access *the service*
- ***gpg ciphertext*** - data encrypted with a *public key* and

Authentication Mechanism

1. *the service* has an internal storage that is encrypted and
2. *The service* is available on the *server* url: `https://r131733.xyz`_:
3. A *user* can join *the service* by acessing  `/join <https://r131733.xyz/join>`_:
   1. The *user* provide its *public key*
   2. *The service* validates that the given *public key* matches a *known fingerprint*, blocking the access if unknown.
   3. *The service* generates a unique one-time password and encrypts it using the *user's* *public key*
   4. The *user* is prompted to decrypt a *gpg ciphertext* which shall result in a one-time password
   5. The *user* puts the one-time password in and submits the form
   6. The *user* is now a *member* and its email will be extracted
      from the *public key* metadata for later cross-reference with a *known fingerprint*.
   7. The *user* is now an authenticated *member*
4. A *user* can sign-in *the service* by acessing  `/login <https://r131733.xyz/login>`_:
   1. The *user* is prompted with its email address, which shall belong to a *known fingerprint*.
   2. The *user* is prompted to decrypt a *gpg ciphertext* which shall result in a one-time password
   3. The *user* puts the one-time password in and submits the form
   4. The *user* is now an authenticated *member*
