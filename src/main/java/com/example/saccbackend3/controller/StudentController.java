package com.example.saccbackend3.controller;

import com.example.saccbackend3.entity.Student;
import com.example.saccbackend3.service.StudentService;
import org.apache.ibatis.annotations.Param;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
/**
 *
 * @author TX
 * @date 2022/3/24 12:53
 */
@RestController
public class StudentController {
    @Autowired
    StudentService studentService;

    /**
     * 增加学生
     * @param student
     * @return
     */
    @PostMapping("/add")
    public String add(@RequestBody Student student){
        //todo
         if (studentService.addStudent(student))
            return "新增成功!";
         else
             return "新增失败!";
    }

    /**
     * 根据 id 删除学生
     * @param id
     * @return
     */
    @DeleteMapping("/delete/{id}")
    public String delete(@PathVariable("id") String id){
        //todo
        if (studentService.deleteStudentById(id))
            return "删除成功!";
        else
            return "删除失败!";
    }

    /**
     * 更新学生信息
     * @param student
     * @return
     */
    @PutMapping("/update")
    public String update(@RequestBody Student student){
        //todo
        if (studentService.updateStudent(student))
            return "修改成功!";
        else
            return "修改失败!";
    }

    /**
     * 获取所有的学生信息
     * @return
     */
    @GetMapping("/get")
    public List<Student> get(){
        //todo

        return studentService.listStudent();
    }

    /**
     * 根据给定的年龄段查找学生
     * @param start
     * @param end
     * @return
     */
    @GetMapping("/getByAge/{start}/{end}")
    public List<Student> findByAge(@PathVariable("start") Integer start, @PathVariable("end") Integer end){
        //todo

        return studentService.listStudentByAges(start, end);
    }
}
