FROM python:3.11-slim

# Install system dependencies for OpenGL and graphics
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglu1-mesa \
    libgles2-mesa \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    build-essential \
    cmake \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install pybind11 (header-only)
RUN pip install pybind11

# Copy pybind11 for C++ build
COPY external/pybind11 ./external/pybind11

# Copy CMakeLists.txt for C++ build
COPY CMakeLists.txt ./CMakeLists.txt

# Copy C++ bindings source files
COPY src/bindings ./src/bindings

# Build C++ bindings
COPY scripts/build_cpp.sh ./scripts/build_cpp.sh
RUN chmod +x ./scripts/build_cpp.sh && ./scripts/build_cpp.sh

# Copy application code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/storage /app/logs /app/cache

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 