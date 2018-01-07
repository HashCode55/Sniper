import click
from click.testing import CliRunner
import unittest 

from sniper.sniper import sniper



class TestSniperClientCommands(unittest.TestCase):		
	"""
	Tests all the commands in sniper 
	"""
	# class global CLI Runner
	runner = CliRunner()		
	# insert some snippets for testing 
	runner.invoke(sniper, ['new', '-t'], input='test_name\ntest_desc\ntest_code')
	runner.invoke(sniper, ['new', '-t'], input='test_edit\ntest_desc\ntest_code')						
	runner.invoke(sniper, ['new', '-t', '-e'], input='test_run\ntest_desc\nls')

	def test_new(self):	
		result = self.runner.invoke(sniper, ['new', '-t'], input='test_new\ntest_desc\ntest_code')				
		assert result.exit_code == 0
		# check if the test snippet has been inserted or not
		result = self.runner.invoke(sniper, ['get', 'test_new'])	    	    
		assert result.exit_code == 0
		assert 'Snippet successfully copied to clipboard.' in result.output	    

	def test_get(self):	    	   
	    result = self.runner.invoke(sniper, ['get', 'test_name'])	    	    
	    assert result.exit_code == 0
	    assert 'Snippet successfully copied to clipboard.' in result.output

	def test_get_fail(self):		
		result = self.runner.invoke(sniper, ['get', 'ls not'])	    		
		assert result.exit_code == 1		
		assert 'No snippet exists' in result.output

	def test_ls(self):
		result = self.runner.invoke(sniper, ['ls'])
		assert result.exit_code == 0
		assert 'test_name' in result.output

	def test_cat(self):
		result = self.runner.invoke(sniper, ['cat', 'test_name'])
		assert result.exit_code == 0
		assert 'test_code' in result.output
	
	def test_edit(self):		
		result = self.runner.invoke(sniper, ['edit', 'test_edit', '-t'], input='\n\n\ntest_code_change')				
		assert result.exit_code == 0
		assert 'Snippet successfully edited.' in result.output 
		result = self.runner.invoke(sniper, ['cat', 'test_edit'])
		assert result.exit_code == 0
		assert 'test_code_change' in result.output
	
	def test_find(self):
		result = self.runner.invoke(sniper, ['find', 'test_edit'], input='\n\n\ntest_code_change')				
		assert result.exit_code == 0
		assert 'test_edit' in result.output

	def test_run(self):
		result = self.runner.invoke(sniper, ['run', 'test_run'])
		assert result.exit_code == 0

	def test_rm(self):
		result = self.runner.invoke(sniper, ['rm', 'test_name'])
		assert result.exit_code == 0
		assert 'Snippet successfully deleted.' in result.output
		result = self.runner.invoke(sniper, ['cat', 'test_name'])
		assert 'No snippet exists' in result.output
		
if __name__ == '__main__':
	unittest.main()
