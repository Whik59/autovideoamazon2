python run_pipeline.py sv Svensktech


dont forget to run THE AUTHENTIFICATION of the app frst for youtube api

python step5_youtube_uploader.py de --channel top3kuche --secrets-path credentials/top3kuche.json


vérification thumbnail aussi si new channel
python run_pipeline.py fr top3cuisine --max-videos 4
python run_pipeline.py de top3kuche --start-date 2025-09-16 --max-videos 6

python run_pipeline.py de top3kaffee --start-date 2025-09-16 --max-videos 4 --num-workers 4
