import unittest
import subprocess
import app.text_cat_server as s

apps = [
	  'is-invalid-batch.py'
	, 'waste-metric.py'
	, 'one-swap-recommendation.py'
	, 'two-swap-recommendation.py'
]

def myrun(cmd, par):
	stdout = []
	proc = subprocess.Popen(['python', cmd, par], stdout=subprocess.PIPE)
	while True:
		line = proc.stdout.readline()
		if not line:
			break
		stdout.append(line.decode('utf-8').rstrip())
	proc.stdout.close()
	proc.terminate()
	return stdout

class TestBatchValidity(unittest.TestCase):
	def test_bad_format(self):
		for a in apps:
			out = myrun(a, 'bad-data-format.json')
			self.assertEqual(out[0], 'Bad format! Cannot convert to JSON!')

	def test_sample_data(self):
		files = [
			('../sample-data/batch-00.json', False)
			, ('../sample-data/batch-01.json', False)
			, ('../sample-data/batch-02.json', False)
			, ('../sample-data/batch-03.json', False)
			, ('../sample-data/batch-04.json', False)
			, ('../sample-data/batch-05.json', False)
			, ('../sample-data/batch-06.json', False)
			, ('../sample-data/batch-07.json', False)
			, ('../sample-data/batch-08.json', False)
			, ('../sample-data/batch-09.json', False)
			, ('../sample-data/batch-10.json', False)
			, ('../sample-data/batch-11.json', False)
			, ('../sample-data/batch-12.json', False)
			, ('../sample-data/batch-13.json', False)
			, ('../sample-data/batch-14.json', True)
			, ('../sample-data/batch-15.json', True)
			, ('../sample-data/batch-16.json', True)
			, ('../sample-data/batch-17.json', True)
			, ('../sample-data/batch-18.json', True)
			, ('../sample-data/batch-19.json', True)
			, ('optimum-sample.json', False)
			, ('one-to-optimum-sample.json', False)
		]
		for f in files:
			out = myrun('is-invalid-batch.py', f[0])
			self.assertEqual( out[0], 'Batch is not valid!' if f[1] else 'Valid Batch')
	
	def test_waste_metric_calc(self):
		files = [
			('../sample-data/batch-00.json', 335)
			, ('optimum-sample.json', 9)
			, ('one-to-optimum-sample.json', 11)
		]
		for f in files:
			deck = ds.read_file(['', f[0]])
			conv_deck = ds.json_to_tuples(deck)
			self.assertEqual( ds.get_waste_metric(conv_deck), f[1])

	def test_one_swap_recommendation(self):
		files = [
			('../sample-data/batch-00.json', ((5, 15), 274))
			, ('optimum-sample.json', ((None, None), 9))
			, ('one-to-optimum-sample.json', ((2, 3), 9))
		]
		for f in files:
			deck = ds.read_file(['', f[0]])
			conv_deck = ds.json_to_tuples(deck)
			original_waste_metric = ds.get_waste_metric(conv_deck)
			self.assertEqual(ds.try_all_swaps(conv_deck, original_waste_metric), f[1])

	def test_two_swap_recommendation_optimum(self):
		for a in apps:
			out = myrun('two-swap-recommendation.py', 'optimum-sample.json')
			self.assertEqual(out[0], 'Further waste metric reduction is not possible!')
	
	def test_two_swap_recommendation_1to_optimum(self):
		for a in apps:
			out = myrun('two-swap-recommendation.py', 'one-to-optimum-sample.json')
			self.assertEqual(out[0], 'By swapping AS and AH, you could reduce waste metric from 11 to 9.')
			self.assertEqual(out[1], 'Further waste metric reduction is not possible!')

if __name__ == '__main__':
	unittest.main()