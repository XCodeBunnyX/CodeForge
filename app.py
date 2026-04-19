"""
GFG Auto-Solver v4.2 - CRITICAL FIX FOR EXTRA CLASS DEFINITIONS
================================================================

FIX v4.2:
  - CRITICAL: AI now explicitly told to NOT define helper classes
  - Groq was outputting TreeNode, Node, etc. even though GFG provides them
  - New prompt: "Do NOT define any classes. Only implement the method body."
  - Detects and removes extra class definitions from AI output

FIX v4.1:
  - Template preservation and code validation

USAGE:
    python gfg_solver_v4.2.py <GFG_BATCH_URL>
"""

import os, sys, time, re, json, random, tempfile

try:
    import distutils
except:
    try:
        import setuptools._distutils as _distutils
        sys.modules["distutils"] = _distutils
    except:
        pass

from openai import OpenAI
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LANGUAGE = "Java"
MAX_PROBLEMS = 50
WAIT_BETWEEN = 2
SUBMIT_WAIT = 12
MAX_FIX_ATTEMPTS = 3
TYPING_WPM = 8000
TERMINAL_VERBOSE = False
NETWORK_TIMEOUT = 30

def vprint(msg):
    if TERMINAL_VERBOSE: print(msg)

def setup_ai():
    if not GROQ_API_KEY:
        print("[ERROR] GROQ_API_KEY not set")
        sys.exit(1)
    return OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

def setup_browser():
    print("[INFO] Launching browser...")
    user_data_dir = tempfile.mkdtemp(prefix="gfg_")
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument(f"--user-data-dir={user_data_dir}")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    except:
        driver = uc.Chrome(options=opts, use_subprocess=True)
    driver.set_page_load_timeout(180)
    driver.implicitly_wait(5)
    time.sleep(2)
    return driver

def is_session_alive(driver):
    try:
        _ = driver.current_url
        return True
    except:
        return False

def dismiss_sidebar(driver):
    if not is_session_alive(driver): return
    try:
        driver.execute_script("""
            var overlays = document.querySelectorAll('[class*="sidebar"], [class*="overlay"]');
            overlays.forEach(el => { el.style.display='none'; el.style.pointerEvents='none'; });
        """)
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except: pass

def count_delimiters(text, open_ch, close_ch):
    opens = closes = 0
    state = "code"
    i = 0
    while i < len(text):
        c = text[i]
        if state == "line":
            if c == '\n': state = "code"
            i += 1
            continue
        if state == "block":
            if c == '*' and i+1 < len(text) and text[i+1] == '/': state = "code"; i += 2
            else: i += 1
            continue
        if state in ("dquote", "squote"):
            q = '"' if state == "dquote" else "'"
            if c == '\\' and i+1 < len(text): i += 2; continue
            if c == q: state = "code"
            i += 1
            continue
        if c == '/' and i+1 < len(text):
            if text[i+1] == '/': state = "line"; i += 2; continue
            if text[i+1] == '*': state = "block"; i += 2; continue
        if c == '"': state = "dquote"; i += 1; continue
        if c == "'": state = "squote"; i += 1; continue
        if c == open_ch: opens += 1
        if c == close_ch: closes += 1
        i += 1
    return opens, closes

def remove_extra_classes(code):
    """
    CRITICAL FIX: Remove any class definitions that AI added.
    GFG provides TreeNode, Node, ListNode, etc.
    We only need the Solution method implementation.
    """
    lines = code.split('\n')
    output = []
    skip_class = False
    brace_count = 0
    
    for line in lines:
        # Detect class definition (except Solution)
        if 'class ' in line and 'Solution' not in line:
            skip_class = True
            brace_count = 0
            print(f"[FIX] Removing extra class: {line.strip()[:50]}")
            continue
        
        # Track braces while skipping class
        if skip_class:
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
                skip_class = False
            continue
        
        output.append(line)
    
    # Remove trailing extra braces
    result = '\n'.join(output).rstrip()
    while result.endswith('}') and result.count('{') == result.count('}'):
        result = result.rstrip()[:-1].rstrip()
    
    return result.strip()

def fix_extra_braces(code, template=""):
    for open_ch, close_ch in [('{', '}'), ('(', ')')]:
        c_opens, c_closes = count_delimiters(code, open_ch, close_ch)
        extra = c_closes - c_opens
        if extra > 0:
            lines = code.rstrip().split('\n')
            removed = 0
            while removed < extra and lines:
                stripped = lines[-1].strip()
                if stripped == close_ch:
                    lines.pop(); removed += 1
                elif stripped.endswith(close_ch):
                    lines[-1] = lines[-1].rstrip()[:-1].rstrip(); removed += 1
                else:
                    break
            code = "\n".join(lines)
    return code.strip()

def solve_problem(client, problem_text, template, language="Java"):
    """
    FIXED v4.2: Explicitly prevent AI from defining extra classes.
    """
    prompt = f"""You are solving a GeeksforGeeks problem in {language}.

PROBLEM:
{problem_text[:5000]}

TEMPLATE PROVIDED BY GFG:
{template if template.strip() else "(none)"}

**** CRITICAL RULES ****
1. GFG provides the complete class structure.
   Output ONLY the method body code.
   
2. NEVER define any additional classes.
   NOT TreeNode, NOT Node, NOT ListNode, NOT Stack, NOT anything.
   GFG has already defined all helper classes.
   
3. NEVER output the class definition for Solution.
   NEVER output the method signature.
   Output ONLY the implementation code inside the method.
   
4. Balance your braces and parentheses.
   Count them before outputting.
   
5. Do NOT add closing braces after your code.
   
6. Return raw code only. No markdown. No explanation.

CODE (implementation only):"""

    for attempt in range(1, 3):
        try:
            print(f"[AI] Solving (attempt {attempt}/2)...")
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                timeout=NETWORK_TIMEOUT,
            )
            code = response.choices[0].message.content.strip()
            code = re.sub(r"^```[\w]*\n?", "", code)
            code = re.sub(r"\n?```$", "", code)
            
            # CRITICAL FIX v4.2: Remove extra class definitions
            code = remove_extra_classes(code)
            code = fix_extra_braces(code.strip(), template)
            
            print(f"[AI] ✓ Got solution ({len(code)} chars)")
            return code
        except TimeoutError:
            print(f"[AI] ⏱ Timeout...")
            if attempt >= 2: return ""
            time.sleep(1)
        except Exception as e:
            print(f"[ERROR] {e}")
            return ""
    return ""

def strip_indentation(code):
    lines = code.split('\n')
    cleaned = [line.lstrip() for line in lines]
    while cleaned and not cleaned[0].strip(): cleaned.pop(0)
    while cleaned and not cleaned[-1].strip(): cleaned.pop()
    return '\n'.join(cleaned)

def human_type(element, text, wpm=TYPING_WPM):
    base_delay = 60 / (wpm * 5)
    AUTO_CLOSE_OPENERS = {'{', '(', '[', '"', "'"}
    for char in text:
        element.send_keys(char)
        if char in AUTO_CLOSE_OPENERS:
            time.sleep(0.008)
            element.send_keys(Keys.DELETE)
        delay = max(0.0003, random.gauss(base_delay, base_delay * 0.12))
        if char == "\n": delay += 0.001
        time.sleep(delay)

def clear_and_type_solution(driver, code):
    try:
        for sel in ["textarea.ace_text-input", ".monaco-editor textarea"]:
            try:
                textarea = driver.find_element(By.CSS_SELECTOR, sel)
                break
            except:
                continue
        
        driver.execute_script("""
            arguments[0].style.opacity='1'; arguments[0].style.position='fixed';
            arguments[0].style.top='50px'; arguments[0].style.left='50px';
            arguments[0].style.zIndex='99999'; arguments[0].focus();
        """, textarea)
        time.sleep(0.1)
        
        textarea.send_keys(Keys.CONTROL + "a")
        time.sleep(0.04)
        textarea.send_keys(Keys.DELETE)
        time.sleep(0.05)
        
        clean_code = strip_indentation(code)
        print(f"[INFO] Typing {len(clean_code)} chars...")
        human_type(textarea, clean_code)
        return True
    except Exception as e:
        print(f"[ERROR] Typing failed: {e}")
        return False

def validate_before_submit(driver, editor_code):
    bal_ok, msg = delimiter_balance_ok(editor_code)
    if not bal_ok:
        print(f"[VALIDATE] ✗ {msg}")
        return False
    print("[VALIDATE] ✓ Code OK")
    return True

def delimiter_balance_ok(code, language="Java"):
    if not code or len(code) < 5: return False, "too short"
    for open_ch, close_ch in [('{', '}'), ('(', ')'), ('[', ']')]:
        opens, closes = count_delimiters(code, open_ch, close_ch)
        if opens != closes:
            return False, f"{open_ch}{close_ch}: {opens} vs {closes}"
    return True, "balanced"

def extract_problem(driver, max_retries=5):
    if not is_session_alive(driver): return "", ""
    time.sleep(2)
    dismiss_sidebar(driver)
    
    for attempt in range(1, max_retries + 1):
        time.sleep(1)
        
        template = ""
        try:
            template = driver.execute_script("""
                if (typeof ace !== 'undefined') {
                    var ae = document.querySelectorAll('.ace_editor');
                    if (ae.length > 0) { var code = ace.edit(ae[0]).getValue() || '';
                    if (code.length > 5) return code; }
                }
                return '';
            """) or ""
        except: pass
        
        problem_text = ""
        for sel in [".problem-statement", "[class*='problem_content']"]:
            try:
                for el in driver.find_elements(By.CSS_SELECTOR, sel):
                    txt = el.text.strip()
                    if len(txt) > 100:
                        problem_text = txt
                        break
                if problem_text: break
            except: continue
        
        if not problem_text:
            try:
                problem_text = driver.find_element(By.TAG_NAME, "body").text[:5000]
            except: pass
        
        if problem_text and len(problem_text) > 50:
            print(f"[EXTRACT] ✓ Problem ({len(problem_text)} chars) | Template: ({len(template)} chars)")
            return problem_text, template
        
        if attempt < max_retries:
            time.sleep(2)
    
    return problem_text, template

def classify_error(error_text):
    et = (error_text or "").lower()
    if any(k in et for k in ["runtime error", "exception", "nullpointer"]):
        return "RE"
    if any(k in et for k in ["compilation error", "compile error", "syntax error"]):
        return "CE"
    return "OTHER"

def paste_solution(driver, code, language="Java"):
    if not is_session_alive(driver): return False
    dismiss_sidebar(driver)
    time.sleep(0.5)
    
    try:
        for sel in ["[class*='languageDropdown']", "select[class*='lang']"]:
            try:
                dd = driver.find_element(By.CSS_SELECTOR, sel)
                s = Select(dd)
                for opt in s.options:
                    if language.lower() in opt.text.lower():
                        s.select_by_visible_text(opt.text)
                        time.sleep(0.8)
                        break
                break
            except: continue
    except: pass
    
    time.sleep(0.5)
    dismiss_sidebar(driver)
    
    if clear_and_type_solution(driver, code):
        print("[OK] ✓ Code typed.")
        return True
    print("[ERROR] ✗ Could not type.")
    return False

def submit_solution(driver):
    if not is_session_alive(driver): return False
    dismiss_sidebar(driver)
    time.sleep(0.3)
    
    for sel in ["//button[normalize-space()='Submit']", "//button[contains(text(),'Submit')]"]:
        try:
            btn = driver.find_element(By.XPATH, sel)
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                print("[OK] Clicked Submit.")
                return True
        except: continue
    return False

def check_result(driver, max_wait=60):
    print(f"[RESULT] Waiting ({max_wait}s)...")
    deadline = time.time() + max_wait
    
    while time.time() < deadline:
        if not is_session_alive(driver): return "session_dead", ""
        
        for sel in ["[class*='correct']", "//*[contains(text(),'Correct')]"]:
            try:
                if driver.find_element(By.CSS_SELECTOR if '[' in sel else By.XPATH, sel).is_displayed():
                    print("[+] ACCEPTED!")
                    return "accepted", ""
            except: continue
        
        for sel in ["[class*='wrong']", "//*[contains(text(),'Compilation Error')]"]:
            try:
                el = driver.find_element(By.CSS_SELECTOR if '[' in sel else By.XPATH, sel)
                if el.is_displayed():
                    error = el.text.strip()[:300]
                    print(f"[-] REJECTED: {error}")
                    return "rejected", error
            except: continue
        
        time.sleep(2)
    
    return "unknown", ""

def go_back_to_editor(driver):
    try:
        for sel in ["//button[contains(text(),'Back')]", "//button[contains(text(),'Edit')]"]:
            btn = driver.find_element(By.XPATH, sel)
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                print("[<] Back to editor.")
                time.sleep(1.5)
                return True
    except: pass
    return False

def go_to_next(driver):
    try:
        btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class*='next']")))
        driver.execute_script("arguments[0].click();", btn)
        print("[>] Next problem!")
        time.sleep(2)
        return True
    except: pass
    return False

def navigate_to(driver, url):
    print(f"[NAV] Opening: {url}")
    try:
        driver.get(url)
        time.sleep(4)
        if "geeksforgeeks" in driver.current_url:
            print("[OK] ✓ On GFG!")
            time.sleep(2)
            return True
    except: pass
    print("[FATAL] Could not navigate!")
    return False

def main():
    if len(sys.argv) < 2:
        print("\nUsage: python gfg_solver_v4.2.py <GFG_URL>\n")
        sys.exit(1)
    
    print("[INFO] GFG Solver v4.2 - Extra Class Definition Fix")
    client = setup_ai()
    driver = setup_browser()
    
    if not navigate_to(driver, sys.argv[1]):
        sys.exit(1)
    
    solved = failed = 0
    
    for i in range(1, MAX_PROBLEMS + 1):
        print(f"\n{'─'*70}\n  Problem #{i}\n{'─'*70}")
        
        if not is_session_alive(driver):
            print("[FATAL] Session dead!")
            break
        
        print("[1/5] Extracting...")
        problem_text, template = extract_problem(driver)
        if not problem_text:
            print("[ERROR] No problem. Skipping.")
            failed += 1
            if not go_to_next(driver): break
            continue
        
        print(f"[2/5] Solving...")
        code = solve_problem(client, problem_text, template, LANGUAGE)
        if not code:
            print("[ERROR] AI failed. Skipping.")
            failed += 1
            if not go_to_next(driver): break
            continue
        
        problem_accepted = False
        for fix_attempt in range(MAX_FIX_ATTEMPTS):
            print(f"[3/5] Typing (attempt {fix_attempt+1}/{MAX_FIX_ATTEMPTS})...")
            time.sleep(WAIT_BETWEEN)
            if not paste_solution(driver, code, LANGUAGE):
                print("[ERROR] Could not type.")
                break
            
            print(f"[4/5] Validating...")
            if not validate_before_submit(driver, code):
                break
            
            print(f"[5/5] Submitting...")
            time.sleep(WAIT_BETWEEN)
            if not submit_solution(driver):
                break
            
            result, error_text = check_result(driver, SUBMIT_WAIT)
            
            if result == "accepted":
                solved += 1
                problem_accepted = True
                break
            
            if result == "session_dead":
                print("[FATAL] Session crashed!")
                sys.exit(1)
            
            if result in ("rejected", "unknown"):
                if fix_attempt + 1 >= MAX_FIX_ATTEMPTS:
                    failed += 1
                    break
                
                print(f"[FIX] Error: {classify_error(error_text)}")
                if not go_back_to_editor(driver):
                    print("[WARN] Could not go back.")
                time.sleep(1)
        
        if not problem_accepted:
            failed += 1
        
        time.sleep(WAIT_BETWEEN)
        if i < MAX_PROBLEMS:
            if not go_to_next(driver):
                break
            time.sleep(2)
    
    print(f"\n{'═'*70}\n  FINAL: Solved {solved} | Failed {failed}\n{'═'*70}")

if __name__ == "__main__":
    main()