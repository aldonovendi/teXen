from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from . import youtube_api as yt
from . import sentiment_analysis as sa

# Create your views here.
def index(request):
#    if request.method == "POST":
#        url = request.POST.get('url')
#        return JsonResponse({'url':url})
#        return HttpResponseRedirect("#result", kwargs={'url' : url})
#        return render(request, 'personal/home.html', {'url' : url})
#        print('this is a post request')
    
    return render(request, 'personal/home.html')

def result(request):
    if request.method == 'POST':
        url = request.POST['url']
        yt.launch_youtube(url)
        word_scores = sa.create_word_scores()
#        print(yt.commentSample)
        sentimentResult = sa.evaluate_features(yt.commentSample, word_scores)
        print(len(sentimentResult['pos']))
        return JsonResponse({
            'url':url,
            'videoID':yt.videoID,
            'videoTitle':yt.videoTitle,
            'commentCount':yt.commentCount,
            'commentSample':yt.commentSample[:5],
            'sentimentPos':len(sentimentResult['pos']),
            'sentimentNeg':len(sentimentResult['neg']),
            'sentimentNeu':len(sentimentResult['neu']),
        })