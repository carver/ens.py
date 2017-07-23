

def test_finalize_name_to_label(registrar, mocker, fake_hash):
    mocker.patch.object(registrar.web3, 'sha3', side_effect=fake_hash)
    mocker.patch.object(registrar.core, 'finalizeAuction')
    registrar.finalize('theycallmetim.eth')
    registrar.core.finalizeAuction.assert_called_once_with(b'HASH(btheycallmetim)',
                                                           transact={'gas': 120000})
