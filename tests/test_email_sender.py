import pytest
from unittest.mock import patch, Mock
from modules.email_sender import send_email, EmailError

def test_send_email_success():
    """Test successful email sending via Sparkpost"""
    mock_sp = Mock()
    mock_response = {'total_accepted_recipients': 1}
    mock_sp.transmissions.send.return_value = mock_response

    with patch('modules.email_sender.SparkPost', return_value=mock_sp):
        result = send_email(
            api_key='test_key',
            from_email='from@test.com',
            to_email='to@test.com',
            subject='Test Subject',
            html_content='<p>Test</p>'
        )

        assert result == True
        mock_sp.transmissions.send.assert_called_once()

def test_send_email_api_error():
    """Test Sparkpost API error handling"""
    mock_sp = Mock()
    mock_sp.transmissions.send.side_effect = Exception("API Error")

    with patch('modules.email_sender.SparkPost', return_value=mock_sp):
        with pytest.raises(EmailError, match="Failed to send email"):
            send_email('test_key', 'from@test.com', 'to@test.com',
                      'Subject', '<p>Body</p>')
