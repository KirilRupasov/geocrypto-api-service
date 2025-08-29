FROM public.ecr.aws/lambda/python:3.11

# Copy function code
COPY lambda_trends.py ${LAMBDA_TASK_ROOT}

# (Optional) Install dependencies if you have a requirements.txt
# COPY requirements.txt .
# RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the Lambda handler
CMD ["lambda_trends.lambda_handler"]