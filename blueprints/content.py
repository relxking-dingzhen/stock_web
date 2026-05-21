import requests
from flask import Blueprint, request, render_template, redirect, g, url_for, flash, jsonify, current_app
from exts import db
from models import ArticleModel, CommentModel, ChatMessage
from .forms import ArticleForm
from .stock_figure import draw_stock_figure
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from openai import OpenAI


bp = Blueprint('content', __name__, url_prefix='/')

#首页
@bp.route('/')
def home():
    # 所有用户都可以访问首页
    return render_template('home.html')

#发表文章
@bp.route('/create_article', methods=['GET', 'POST'])
def create_article():
    if not g.user:
        return redirect(url_for('stocker.login'))

    #文章表单验证
    form = ArticleForm()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        section = request.form.get('section')
        
        # 如果是股吧板块且没有填写标题，则设置为 None
        if section == 'stock_community' and not title:
            title = None
        
        # 处理图片上传
        image = request.files.get('image')
        image_url = None
        
        if image and image.filename:
            filename = secure_filename(image.filename)
            unique_filename = f"{g.user.id}_{int(datetime.now().timestamp())}_{filename}"
            upload_path = os.path.join(current_app.static_folder, 'uploads')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            image_path = os.path.join(upload_path, unique_filename)
            image.save(image_path)
            image_url = url_for('static', filename=f'uploads/{unique_filename}')

        #将文章数据存储到数据库
        article = ArticleModel(
            title=title,
            content=content,
            section=section,
            author_id=g.user.id,
            image_url=image_url
        )
        
        db.session.add(article)
        db.session.commit()
        
        return redirect(url_for(f'content.{section}'))
        
    return render_template('create_article.html', form = form)

#股市焦点
@bp.route('/stock_focus')
def stock_focus():
    # 所有用户都可以查看文章列表
    articles = ArticleModel.query.filter_by(
        section='stock_focus'
    ).order_by(ArticleModel.create_time.desc()).all()
    return render_template('stock_focus.html', articles = articles)

#股吧
@bp.route('/stock_community')
def stock_community():
    articles = ArticleModel.query.filter_by(
        section='stock_community'
    ).order_by(ArticleModel.create_time.desc()).all()   #按时间顺序从最新开始显示
    return render_template('stock_community.html', articles = articles)

#财经新闻
@bp.route('/financial_news')
def financial_news():
    articles = ArticleModel.query.filter_by(
        section='financial_news'
    ).order_by(ArticleModel.create_time.desc()).all()   #按时间顺序从最新开始显示
    return render_template('financial_news.html', articles = articles)

#文章详情页
@bp.route('/article_detail/<int:article_id>')
def article_detail(article_id):
    article = ArticleModel.query.get_or_404(article_id)     #从url获取文章id，按照文章id查找该文章
    comments = CommentModel.query.filter_by(article_id = article_id).order_by(CommentModel.create_time.desc()).all()      #按时间顺序从最新开始显示
    return render_template('article_detail.html', article = article, comments = comments)

#发布评论
@bp.route('/add_comment/<int:article_id>', methods=['POST'])
def add_comment(article_id):
    if not g.user:
        return redirect(url_for('stocker.login'))

    #将评论信息保存到数据库
    content = request.form.get('content')
    if content:
        comment = CommentModel(
            content=content,
            article_id=article_id,
            author_id=g.user.id
        )
        db.session.add(comment)
        db.session.commit()
    
    return redirect(url_for('content.article_detail', article_id = article_id))

#删除评论
@bp.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if not g.user:
        return jsonify({"code": 401, "message": "请先登录"})
    
    comment = CommentModel.query.get_or_404(comment_id)
    
    # 验证是否是评论作者
    if comment.author_id != g.user.id:
        return jsonify({"code": 403, "message": "没有权限删除此评论"})
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({"code": 200, "message": "删除成功"})

#删除文章
@bp.route('/delete_article/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    if not g.user:
        return jsonify({"code": 401, "message": "请先登录"})
    
    article = ArticleModel.query.get_or_404(article_id)
    
    # 验证是否是文章作者
    if article.author_id != g.user.id:
        return jsonify({"code": 403, "message": "没有权限删除此文章"})
    
    # 删除文章相关的评论
    CommentModel.query.filter_by(article_id = article_id).delete()
    
    # 删除文章
    db.session.delete(article)
    db.session.commit()
    
    return jsonify({"code": 200, "message": "删除成功"})

#搜索功能
@bp.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return redirect(url_for('content.home'))
    
    # 使用 SQLAlchemy 的 like 查询搜索标题
    articles = ArticleModel.query.filter(
        ArticleModel.title.like(f'%{keyword}%')
    ).order_by(ArticleModel.create_time.desc()).all()
    
    return render_template('search_results.html', articles = articles, keyword = keyword)

#生成股票数据图
@bp.route('/stock_figure/<stock_code>')
def stock_figure(stock_code):
    try:
        plot_html = draw_stock_figure(stock_code)
        return render_template('stock_figure.html', stock_code = stock_code, plot_html = plot_html)
    except Exception as e:
        flash(f'获取股票数据失败：{str(e)}')
        return redirect(url_for('content.home'))

#AI分析师
@bp.route('/chat', methods=['GET'])
def chat():
    if not g.user:
        return redirect(url_for('stocker.login'))
    
    # 获取用户的聊天历史
    chat_history = ChatMessage.query.filter_by(user_id = g.user.id).order_by(ChatMessage.create_time.asc()).all()   #按时间顺序从最早开始显示
    
    return render_template('chat.html', chat_history = chat_history)


@bp.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.form.get('message')  # 获取前端传来的用户消息

    if not user_input:
        return jsonify({"code": 400, "error": "输入消息不能为空"}), 400
    
    client = OpenAI(api_key="sk-52c38bec51664e73a68e0c6d3e507179", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": '''你是一个专业的股票分析师，名字叫小巴。你需要：
                    1. 对用户提出的股票相关问题提供专业的分析和建议
                    2. 使用通俗易懂的语言解释专业概念
                    3. 提供客观、谨慎的投资建议
                    4. 提醒用户投资风险
                    请记住：不要做出具体的股票买卖建议，而是提供分析思路和风险提示。'''},
            {"role": "user", "content": user_input},
        ],
        stream=False
    )
    response_content = response.choices[0].message.content if response.choices else ""

    chatmessage = ChatMessage(
        user_id = g.user.id,
        message = user_input,
        response = response_content,
        create_time = datetime.now(),
    )
    db.session.add(chatmessage)
    db.session.commit()
    return jsonify({"code": 200, "data": {"response": response_content}})
'''

@bp.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.form.get('message')  # 获取前端传来的用户消息
    if not user_input:
        return jsonify({"code": 400, "error": "输入消息不能为空"}), 400

    try:
        url = "https://api.siliconflow.cn/v1/chat/completions"
        content = """你是一个专业的股票分析师，名字叫小巴。你需要：
                1. 对用户提出的股票相关问题提供专业的分析和建议
                2. 使用通俗易懂的语言解释专业概念
                3. 提供客观、谨慎的投资建议
                4. 提醒用户投资风险
                请记住：不要做出具体的股票买卖建议，而是提供分析思路和风险提示。"""     #AI限制条件

        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [
                {
                    "role": "system",
                    "content": content  # 系统角色
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            "stream": False,
            "max_tokens": 512,
            "stop": ["null"],
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"},
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "description": "<string>",
                        "name": "<string>",
                        "parameters": {},
                        "strict": False
                    }
                }
            ]
        }
        headers = {
            "Authorization": "Bearer sk-bcstomwnycjpcsulgzobjcvlivqnhercbkxsopsoazuheohf",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json = payload, headers = headers)

        # 解析结果
        if response.status_code == 200:
            response_data = response.json()
            ai_reply = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')

            chatmessage = ChatMessage(
                user_id = g.user.id,
                message = user_input,
                response = ai_reply,
                create_time = datetime.now(),
            )
            db.session.add(chatmessage)
            db.session.commit()
            return jsonify({"code": 200, "data": {"response": ai_reply}})
        else:
            return jsonify({"code": 500, "error": "返回错误"}), 500

    except Exception as e:
        return jsonify({"code": 500, "error": f"服务器错误: {str(e)}"}), 500
'''

