from ens import ens

TEST_NAME = 'arachnid.eth'
assert ens.reverse(ens.resolve(TEST_NAME)) == TEST_NAME
