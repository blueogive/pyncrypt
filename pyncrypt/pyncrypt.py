#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module for fetching/storing encrypted credentials from/to a local file."""

import base64
import dotenv
import os

from getpass import getpass
from pbkdf2 import PBKDF2
from Crypto.Cipher import AES
from Crypto import Random
try:
    import cPickle as pickle
except ImportError:
    import pickle


class KeyStore(object):
    """Securely store/retrieve encrypted key-value pairs to/from files."""

    def __init__(self, salt_seed=None, **kwargs):
        """Instantiate the class, define all required attributes.

        NB: If no value of salt_seed is passed at instantiation, a random
        value will be used and it will not be possible to recover the values
        from the secretsdb_file without it. Instantiating the klass with a
        NULL salt_seed is useful, therefore, if you want to create a KeyStore
        that is only useful for the duration of the current Python process
        (i.e., a one-time-use vault)."""
        if (not salt_seed or len(salt_seed) == 0 or
                isinstance(salt_seed, str) is False):
            self.salt_seed = self._urand2str(8)
        else:
            self.salt_seed = salt_seed
        self.passphrase_file = kwargs.get('passphrase_file') or '.secrets_p'
        self.secretsdb_file = kwargs.get('secretsdb_file') or '.secrets'
        # By default, secrets files can be read/written by user executing
        # the script, read by the user's group, and are inaccessible to world.
        self.file_perm = kwargs.get('file_perm') or 0o640
        self.passphrase_size = kwargs.get('passphrase_size') or 64
        self.key_size = kwargs.get('key_size') or 32
        self.block_size = kwargs.get('block_size') or 16
        self.iv_size = kwargs.get('iv_size') or 16
        self.salt_size = kwargs.get('salt_size') or 8

    def _dcode(self, bstring, encoding='utf-8'):
        """Convert base64 bytes to UTF-8."""
        return base64.b64encode(bstring).decode(encoding)

    def _urand2str(self, nbytes, encoding='utf-8'):
        """Return random bytes from cyptographically random pool."""
        phrase = Random.new().read(nbytes)  # Random bytes
        while len(phrase) % 3 != 0:
            phrase += b"="
        return self._dcode(phrase, encoding)

    def _getsalt4key(self, key, salt=None, size=None):
        """Given a key, return a salt."""
        if not salt:
            salt = self.salt_seed
        if not size:
            size = self.salt_size
        return PBKDF2(key, salt).read(size)

    def _encrypt(self, plaintext, salt):
        """Pad plaintext, then encrypt using randomly initialized cipher.

        NB: Strips trailing whitespace frome plaintext!
        """
        if hasattr(plaintext, 'decode'):
            raise TypeError('Please pass a string value, not bytes.')
        # Initialize cipher randomly
        iv = Random.new().read(self.iv_size)
        passphrase = self._getsetphrase()
        # Prepare cipher key
        key = self._getsalt4key(passphrase, salt, size=self.key_size)
        # Pad and encrypt
        mplyr = self.block_size - (len(plaintext) % self.block_size)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        safesecret = cipher.encrypt(plaintext + (r' ' * mplyr))
        return iv + safesecret

    def _decrypt(self, ciphertext, salt):
        """Reconstruct the cipher object and decrypt.

        NB: Strips trailing whitespace from the retrieved value!
        """
        passphrase = self._getsetphrase()
        # Prepare cipher key:
        key = self._getsalt4key(passphrase, salt, size=self.key_size)
        # Reconstruct cipher (IV need not be identical to encrypt version)
        iv = Random.new().read(self.iv_size)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        cleartext = cipher.decrypt(ciphertext)[len(iv):]
        try:
            retval = cleartext.decode().rstrip(r' ')
        except UnicodeDecodeError:
            emsg = ('Value cannot be decoded. The passphrase used to'
                    ' initiate the KeyStore has likely changed. Correct'
                    ' the passphrase to its original value or delete the'
                    ' KeyStore and store new values within it.')
            raise ValueError(emsg)
        return retval

    def _getphrase(self):
        """Getter for passphrase."""
        with open(self.passphrase_file, 'r') as fle:
            return fle.read()

    def _setphrase(self):
        """Setter for passphrase."""
        with open(self.passphrase_file, 'w') as fle:
            os.chmod(self.passphrase_file, self.file_perm)
            fle.write(self._urand2str(self.passphrase_size))
        try:
            # If the passphrase has to be regenerated, then the old secrets
            # file is irretrievable and should be removed
            if os.path.exists(self.secretsdb_file):
                os.remove(self.secretsdb_file)
        except:
            raise
        return None

    def _getsetphrase(self):
        """Get/Set brancher for passphrase."""
        if os.path.exists(self.passphrase_file):
            passphrase = self._getphrase()
        else:
            self._setphrase()
            passphrase = self._getphrase()
        return passphrase

    def _getsetdb(self):
        """Load or create secrets database."""
        try:
            with open(self.secretsdb_file, 'rb') as fle:
                dbs = pickle.load(fle)
        except (IOError, EOFError, TypeError):
            dbs = {}
            self._pickledb(dbs)
        return dbs

    def _pickledb(self, thedict):
        with open(self.secretsdb_file, 'wb') as fle:
            os.chmod(self.secretsdb_file, self.file_perm)
            pickle.dump(thedict, fle)
        return None

    def store(self, key, value):
        """Store key-value pair safely and save to disk."""
        dbs = self._getsetdb()
        dbs[key] = self._encrypt(value, self._getsalt4key(key))
        self._pickledb(dbs)
        return None

    def retrieve(self, key):
        """Fetch key-value pair."""
        dbs = self._getsetdb()
        return self._decrypt(dbs[key], self._getsalt4key(key))

    def require(self, key):
        """Test if key is stored, if not, prompt the user for it.

        Hide their input from shoulder-surfers.
        """
        dbs = self._getsetdb()
        if key not in dbs:
            self.store(key, getpass('Enter a value for "%s":' % key))
        return self.retrieve(key)

    def remove(self, key):
        """Remove a specific key from the store.

        If the key does not exist, catch the error silently.
        """
        dbs = self._getsetdb()
        try:
            val = dbs.pop(key)
            del val
        except KeyError:
            pass
        self._pickledb(dbs)
        return None

    def clear(self):
        """Remove ALL key-value pairs from the store."""
        dbs = self._getsetdb()
        dbs.clear()
        self._pickledb(dbs)
        return None

    def destroy(self):
        """Remove ALL key-value pairs from the store and remove the files."""
        try:
            self.clear()
            os.remove(self.secretsdb_file)
            os.remove(self.passphrase_file)
        except:
            raise
        return None


def main(vault, keyname):
    """Return keyname entry from vault in plain text."""
    return vault.require(keyname)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--env', default=dotenv.find_dotenv(), dest='env',
                   help='Environment file (default: %(default)s)')
    p.add_argument('--passphrase_varname', default='PASSPHRASE',
                   dest='passphrase',
                   help='Name of variable in environment file defining ' +
                        'passphrase for the encryption algo ' +
                        '(default: %(default)s).')
    p.add_argument(dest='key',
                   help='Name of key for which the decrypted value should ' +
                        'be returned.')
    cliargs = p.parse_args()
    dotenv.load_dotenv(cliargs.env)
    VLT = KeyStore(os.environ[cliargs.passphrase])
    rv = main(VLT, cliargs.key)
    print(rv)
