USE employees;

/* 1. Extract all employees from the sales department. */
/*SELECT DISTINCT emp_no, dept_name
       FROM dept_emp
       JOIN departments
       ON departments.dept_no = dept_emp.dept_no
       AND dept_name LIKE 'sales'
       LIMIT 20;
*/

/* 2. Extract all employees from the engineering department with salaies ranging from 100K to 200K. */
/*SELECT employees.emp_no, employees.first_name, employees.last_name, 
       titles.title, salaries.salary, salaries.to_date AS salary_to_date
       FROM titles
       LEFT JOIN employees
       	    ON employees.emp_no = titles.emp_no
	    INNER JOIN salaries
	    ON titles.emp_no = salaries.emp_no
	    AND salaries.salary BETWEEN 100000 AND 200000
       WHERE titles.title LIKE '%engineer%'
       GROUP BY employees.emp_no
       HAVING salary_to_date = MAX(salary_to_date)
       ORDER BY salary DESC
       LIMIT 10;
*/

/* 3. Find all employees whose salary is higher than their managers. */
/*SELECT DISTINCT emp.emp_no
       FROM dept_emp AS emp
       JOIN salaries AS sal_emp
       	    ON emp.emp_no = sal_emp.emp_no
	    JOIN dept_manager AS mgr
       	    ON emp.dept_no = mgr.dept_no
	    JOIN salaries AS sal_mgr
	    ON mgr.emp_no = sal_mgr.emp_no
       WHERE sal_emp.salary > sal_mgr.salary
       LIMIT 20;
*/

/* 4. Find all employees who currently work in the IT department for 1-3 years. */
/* Changed to Research department b/c I don't see an IT dept anywhere. */
SELECT cur_title.emp_no, cur_title.title, cur_title.from_date
    FROM (SELECT emp_no, title, from_date, to_date
      	 FROM titles
         WHERE to_date = '9999-01-01'
	 HAVING DATEDIFF(CURDATE(), from_date) BETWEEN 4380 AND 5475
	 ) cur_title
    INNER JOIN (SELECT dept_emp.emp_no
        FROM departments AS dept
        LEFT JOIN dept_emp
        ON dept.dept_no = dept_emp.dept_no
        WHERE dept.dept_name LIKE '%research%') research
    ON cur_title.emp_no = research.emp_no
    ORDER BY from_date DESC
    LIMIT 30;


