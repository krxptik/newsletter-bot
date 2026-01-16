from ai.prompt import summarise_and_tag
from ai.safe_gen import safe_generate
from google.genai.errors import ClientError
from tqdm import tqdm
import time

def throttled_proc(processed_articles):
    for article in tqdm(processed_articles):
        while True:
            try:
                safe_generate(summarise_and_tag, article)
                break
            except ClientError as e:
                error_block = e.details['error']
                for entry in error_block['details']:

                    if entry['@type'].endswith('QuotaFailure'):
                        if 'PerDay' in entry['violations'][0]['quotaId']:
                            print('Daily limit for requests reached, unable to continue.')
                            return False
                        else:
                            continue

                    if entry['@type'].endswith('RetryInfo'):
                        retry_delay = int(entry['retryDelay'].rstrip('s'))
                        time.sleep(retry_delay + 1)