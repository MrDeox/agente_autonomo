import pytest
from agent.analysis_processor import AnalysisProcessor

@pytest.fixture
def logger():
    return logging.getLogger('test_analysis_processor')

@pytest.fixture
def analysis_processor(logger):
    return AnalysisProcessor(logger)


def test_analyze_code(analysis_processor, logger):
    code = 'def example():
    pass'
    result = analysis_processor.analyze_code(code)
    assert 'Analysis Result for Code: def example():
    pass' in result
    logger.info(f'Test result: {result}')


def test_process_analysis(analysis_processor, logger):
    analysis_result = 'Sample analysis result'
    result = analysis_processor.process_analysis(analysis_result)
    assert 'Processed Analysis Result: Sample analysis result' in result
    logger.info(f'Test result: {result}')