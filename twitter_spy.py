import shutil
import os
import sys
import json

import twitter
import preprocessor
import pytextrank


DEFAULT_TWEETS_COUNT_TO_RETRIEVE=20
OUTOUT_DIRECTORY='out'
TWEETS_JSON=OUTOUT_DIRECTORY+'/tweets.json'
STATISTICAL_PARSING_OUTPUT=OUTOUT_DIRECTORY+'/statistical_parsing.json'
KEY_PHRASES_NORMALIZATION_OUTPUT=OUTOUT_DIRECTORY+'/key_phrases_normalization.json'
MAX_SUBJECTS_TO_SHOW=10


CONSUMER_KEY=os.environ['CONSUMER_KEY']
CONSUMER_SECRET=os.environ['CONSUMER_SECRET']
ACCESS_TOKEN_KEY=os.environ['ACCESS_TOKEN_KEY']
ACCESS_TOKEN_SECRET=os.environ['ACCESS_TOKEN_SECRET']


if len(sys.argv) < 2:
	raise ValueError('At least a user name must be provided')
USER_NAME = sys.argv[1]
TWEETS_COUNT = int(sys.argv[2]) if len(sys.argv) > 2 else None


print('Validating twitter API credentials...')
api = twitter.Api(consumer_key=CONSUMER_KEY,
  consumer_secret=CONSUMER_SECRET,
  access_token_key=ACCESS_TOKEN_KEY,
  access_token_secret=ACCESS_TOKEN_SECRET)
print('Validating twitter API credentials... - Done')


tweets_to_retrieve = TWEETS_COUNT if TWEETS_COUNT else DEFAULT_TWEETS_COUNT_TO_RETRIEVE
print('Retrieving up to %d tweets for the user %s...' % (tweets_to_retrieve, USER_NAME))
all_tweets = []
new_tweets = api.GetUserTimeline(screen_name=USER_NAME, count=TWEETS_COUNT)
all_tweets.extend(new_tweets)
oldest_tweet_id = all_tweets[-1].id - 1
while len(new_tweets) > 0 and len(all_tweets) < TWEETS_COUNT:
	print("Getting tweets before %s" % (oldest_tweet_id))	
	new_tweets = api.GetUserTimeline(screen_name=USER_NAME, count=TWEETS_COUNT-len(all_tweets), max_id=oldest_tweet_id)
	all_tweets.extend(new_tweets)
	oldest_tweet_id = all_tweets[-1].id - 1	
	print("...%s tweets downloaded so far" % (len(all_tweets)))
user_tweets = [preprocessor.clean(tweet.text) for tweet in all_tweets]
print('Retrieved %d tweets for the user %s... - Done' % (len(user_tweets), USER_NAME))


if os.path.exists(OUTOUT_DIRECTORY):
	shutil.rmtree(OUTOUT_DIRECTORY)
os.makedirs(OUTOUT_DIRECTORY)


print('Saving tweets to json...')
with open(TWEETS_JSON, 'w', encoding='utf8') as outfile:
	json.dump({'id': '777', 'text': '. '.join(user_tweets)}, outfile, ensure_ascii=False)
print('Saving tweets to json - Done')


print('Performing statistical parsing/tagging on tweets...')
with open(STATISTICAL_PARSING_OUTPUT, 'w') as f:
    for graf in pytextrank.parse_doc(pytextrank.json_iter(TWEETS_JSON)):
        f.write("%s\n" % pytextrank.pretty_print(graf._asdict()))
print('Performing statistical parsing/tagging on tweets... - Done')


print('Collect and normalizing the key phrases from the parsed document...')
graph, ranks = pytextrank.text_rank(STATISTICAL_PARSING_OUTPUT)
pytextrank.render_ranks(graph, ranks)
with open(KEY_PHRASES_NORMALIZATION_OUTPUT, 'w') as f:
    for rl in pytextrank.normalize_key_phrases(STATISTICAL_PARSING_OUTPUT, ranks):
        f.write("%s\n" % pytextrank.pretty_print(rl._asdict()))
print('Collect and normalizing the key phrases from the parsed document... - Done')


print("Summarizing tweets based on key phrases...")
phrases = ", ".join(set([p for p in pytextrank.limit_keyphrases(KEY_PHRASES_NORMALIZATION_OUTPUT, phrase_limit=MAX_SUBJECTS_TO_SHOW)]))
print("**Top-10 subjects:** %s" % phrases)
