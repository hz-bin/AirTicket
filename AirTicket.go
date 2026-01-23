package main

import (
	"encoding/json"
	"flag"
	"io"
	"log"
	"math/rand"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"time"
)

type Query struct {
	From string `json:"from"`
	To   string `json:"to"`
	Date string `json:"date"`
}

type Config struct {
	Queries []Query `json:"queries"`
}

var timeWindows = [][2]int{
	{10, 12},
	{14, 16},
	{18, 20},
}

func main() {
	// 定义命令行标志
	once := flag.Bool("once", false, "立即执行一次查询，完成后退出（非守护模式）")
	flag.Parse()

	rand.Seed(time.Now().UnixNano())
	baseDir := getBaseDir()
	logger, logFile := initLogger(baseDir)
	defer logFile.Close()

	logger.Println("scheduler started")

	// 如果指定了 -once 参数，执行一次后退出
	if *once {
		logger.Println("running in once mode (immediate execution)")
		runAllQueries(baseDir, logger)
		logger.Println("once mode completed, exiting")
		return
	}

	// 默认后台运行模式（守护进程）
	logger.Println("running in daemon mode (scheduled execution)")
	for {
		now := time.Now()
		plan := buildPlan(now)

		for _, runAt := range plan {
			logger.Printf("next run: %s", runAt.Format("2006-01-02 15:04:05"))
			sleepUntil(runAt)
			runAllQueries(baseDir, logger)
		}
	}
}

func getBaseDir() string {
	exe, err := os.Executable()
	if err != nil {
		cwd, _ := os.Getwd()
		return cwd
	}
	return filepath.Dir(exe)
}

func findPython(baseDir string) string {
	venvPython := filepath.Join(baseDir, ".venv", "Scripts", "python.exe")
	if _, err := os.Stat(venvPython); err == nil {
		return venvPython
	}
	return "python"
}

func initLogger(baseDir string) (*log.Logger, *os.File) {
	logsDir := filepath.Join(baseDir, "logs")
	_ = os.MkdirAll(logsDir, 0o755)
	logPath := filepath.Join(logsDir, "scheduler.log")
	file, err := os.OpenFile(logPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
	if err != nil {
		log.Fatalf("open log file: %v", err)
	}
	mw := io.MultiWriter(os.Stdout, file)
	logger := log.New(mw, "", log.LstdFlags)
	return logger, file
}

func loadConfig(baseDir string) (Config, error) {
	var cfg Config
	data, err := os.ReadFile(filepath.Join(baseDir, "config.json"))
	if err != nil {
		return cfg, err
	}
	err = json.Unmarshal(data, &cfg)
	return cfg, err
}

func scheduleForDate(day time.Time) []time.Time {
	slots := make([]time.Time, 0, len(timeWindows))
	for _, window := range timeWindows {
		start := time.Date(day.Year(), day.Month(), day.Day(), window[0], 0, 0, 0, day.Location())
		end := time.Date(day.Year(), day.Month(), day.Day(), window[1], 0, 0, 0, day.Location())
		dur := end.Sub(start)
		if dur <= 0 {
			continue
		}
		offset := time.Duration(rand.Int63n(int64(dur)))
		slots = append(slots, start.Add(offset))
	}
	return slots
}

func buildPlan(now time.Time) []time.Time {
	schedule := scheduleForDate(now)
	future := make([]time.Time, 0, len(schedule))
	for _, t := range schedule {
		if t.After(now) {
			future = append(future, t)
		}
	}
	if len(future) == 0 {
		future = scheduleForDate(now.AddDate(0, 0, 1))
	}
	sort.Slice(future, func(i, j int) bool { return future[i].Before(future[j]) })
	return future
}

func sleepUntil(target time.Time) {
	for {
		remaining := time.Until(target)
		if remaining <= 0 {
			return
		}
		step := time.Minute
		if remaining < step {
			step = remaining
		}
		time.Sleep(step)
	}
}

func runAllQueries(baseDir string, logger *log.Logger) {
	cfg, err := loadConfig(baseDir)
	if err != nil {
		logger.Printf("load config failed: %v", err)
		return
	}
	if len(cfg.Queries) == 0 {
		logger.Println("no queries configured")
		return
	}
	for _, q := range cfg.Queries {
		runQuery(baseDir, q, logger)
	}
}

func runQuery(baseDir string, q Query, logger *log.Logger) {
	if q.From == "" || q.To == "" || q.Date == "" {
		logger.Printf("skip invalid query: %+v", q)
		return
	}
	logger.Printf("run query %s -> %s %s", q.From, q.To, q.Date)
	pythonBin := findPython(baseDir)
	cmd := exec.Command(pythonBin, filepath.Join(baseDir, "query.py"), "--from", q.From, "--to", q.To, "--date", q.Date, "--headless")
	cmd.Dir = baseDir
	cmd.Stdout = logger.Writer()
	cmd.Stderr = logger.Writer()
	if err := cmd.Run(); err != nil {
		logger.Printf("query failed: %v", err)
		return
	}
	logger.Printf("query done")
}
