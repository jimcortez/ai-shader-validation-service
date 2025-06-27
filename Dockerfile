FROM python:3.11-slim

# Install system dependencies including OpenGL development libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    freeglut3-dev \
    libglew-dev \
    libglfw3-dev \
    libglm-dev \
    build-essential \
    cmake \
    make \
    g++ \
    curl \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all external dependencies (pybind11, VVISF-GL, etc.) BEFORE build
COPY external ./external

# Copy requirements and install Python dependencies
COPY requirements/requirements-dev.txt .
COPY requirements/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install pybind11 (header-only)
RUN pip install pybind11

# Copy CMakeLists.txt for C++ build
COPY CMakeLists.txt ./CMakeLists.txt

# Copy C++ source files
COPY src/bindings ./src/bindings

# Copy build script
COPY scripts/build_cpp.sh ./scripts/build_cpp.sh

# Build C++ bindings
RUN chmod +x ./scripts/build_cpp.sh && ./scripts/build_cpp.sh

# Copy application source
COPY src/ ./src/
COPY tests/ ./tests/

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