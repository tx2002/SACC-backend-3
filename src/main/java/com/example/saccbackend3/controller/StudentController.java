package com.example.saccbackend3.controller;

import com.example.saccbackend3.entity.Student;
import com.example.saccbackend3.service.StudentService;
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
    public String add(Student student){
        //todo
        return null;
    }

    /**
     * 根据 id 删除学生
     * @param id
     * @return
     */
    @DeleteMapping("/delete")
    public String delete(String id){
        //todo
        return null;
    }

    /**
     * 更新学生信息
     * @param student
     * @return
     */
    @PutMapping("/update")
    public String update(Student student){
        //todo
        return null;
    }

    /**
     * 获取所有的学生信息
     * @return
     */
    @GetMapping("/get")
    public List<Student> get(){
        //todo
        return null;
    }

    /**
     * 根据给定的年龄段查找学生
     * @param start
     * @param end
     * @return
     */
    @GetMapping("/getByAge")
    public List<Student> findByAge(int start, int end){
        //todo
        return null;
    }
}
