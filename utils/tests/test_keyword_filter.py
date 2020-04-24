from utils.keyword_filter import _expand_terms
from utils.keyword_filter import expand_terms


def test__expand_terms_one_first_term():
    expanded_terms = _expand_terms(['video'], ['chat', 'call'])
    expected_result = ['video chat', 'video chats', 'video call', 'video calls']
    assert sorted(expanded_terms) == sorted(expected_result)


def test__expand_terms_two_first_terms():
    expanded_terms = _expand_terms(['video', 'skype'], ['chat', 'call'])
    expected_result = ['video chat', 'video chats', 'video call', 'video calls',
                       'skype chat', 'skype chats', 'skype call', 'skype calls']
    assert sorted(expanded_terms) == sorted(expected_result)


def test__expand_terms_no_second_terms():
    first_terms = ['video', 'skype']
    expanded_terms = _expand_terms(['video', 'skype'])
    assert sorted(expanded_terms) == sorted(first_terms)


def test_expand_terms():
    expanded_terms = expand_terms([[['video', 'skype'], ['chat', 'call']]]*2)
    expected_result = ['video chat', 'video chats', 'video call', 'video calls',
                       'skype chat', 'skype chats', 'skype call', 'skype calls']*2
    assert sorted(expanded_terms) == sorted(expected_result)

