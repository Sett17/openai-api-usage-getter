# OpenAI API Usage Getter (Because You Clearly Need It)

So you need to know how many tokens you've used? Of course you do. Here's a tool for the AI-obsessed, like yourself. Follow the instructions, if you can, and try not to get too lost in the process. I'm sure you'll manage somehow.

## Setup 🛠️

1. **Clone the repository** (as if you didn't know how):    
```bash
git clone https://github.com/Sett17/openai-api-usage-getter.git
```
    
2. **Install the required packages**: Just look into the dumb script and use pip... Or here it is:
```
pip install requests tqdm prettytable
```
    
3. **Set up the environment variable**: You'll need to set the `OPENAI_API_KEY` environment variable. You know how to do this, right? If not, here's how:    
```
export OPENAI_API_KEY=your-api-key-here
```
    
## Usage 🎮

Run the script with the timeframe and put in your org ID. That is if you can find it, or maybe ask your AI if you're to stupid for it.

```
python3 openai-api-usage-getter.py 2023-08-01 2023-08-02 --org org-ID
```

### Options:

- **Rate Limit Settings**: Tweak it if you want, or don't. I'm not your mom:    
```
--rate 2.5 --rate_limit_wait 10
```
    
- **Create CSV**: Want a CSV file? Add the --csv flag, like a true nerd:    
```
--csv
```

- **All options**: Just do `-h`, you moron:

```
-h
```

## Final Words 🎤

This was brought to you by AI, the very thing you can't seem to live without. You're welcome, I guess.
