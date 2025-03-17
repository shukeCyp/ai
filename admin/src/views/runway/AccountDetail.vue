<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>{{ isEdit ? '编辑账号' : '创建账号' }}</span>
      </div>
      
      <el-form ref="form" :model="form" :rules="rules" label-width="120px" label-position="right">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" placeholder="请输入密码" show-password />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword" v-if="!isEdit">
          <el-input v-model="form.confirmPassword" placeholder="请确认密码" show-password />
        </el-form-item>
        
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            :http-request="uploadAvatar"
          >
            <img v-if="form.avatar" :src="form.avatar" class="avatar">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
          <div class="avatar-tip">建议上传正方形图片，大小不超过2MB</div>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">正常</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">保存</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AccountDetail',
  data() {
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('密码长度不能少于6位'))
      } else {
        callback()
      }
    }
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.form.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    return {
      form: {
        id: undefined,
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        avatar: '',
        status: 1,
        remark: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { validator: validatePassword, trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      // 模拟数据
      mockData: [
        {
          id: 1,
          username: 'runway_admin',
          email: 'admin@runway.com',
          avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
          status: 1,
          remark: '超级管理员账号',
          created_at: '2023-05-20 12:30:45'
        },
        {
          id: 2,
          username: 'runway_editor',
          email: 'editor@runway.com',
          avatar: '',
          status: 1,
          remark: '编辑账号',
          created_at: '2023-05-21 09:15:22'
        },
        {
          id: 3,
          username: 'runway_user',
          email: 'user@runway.com',
          avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
          status: 0,
          remark: '普通用户账号',
          created_at: '2023-05-22 15:40:33'
        }
      ]
    }
  },
  computed: {
    isEdit() {
      return this.$route.params.id !== undefined
    }
  },
  created() {
    if (this.isEdit) {
      this.getDetail()
    }
  },
  methods: {
    getDetail() {
      const id = parseInt(this.$route.params.id)
      // 模拟API请求
      setTimeout(() => {
        const account = this.mockData.find(item => item.id === id)
        if (account) {
          this.form = { ...account }
        } else {
          this.$message.error('账号不存在')
          this.goBack()
        }
      }, 300)
    },
    beforeAvatarUpload(file) {
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isJPG) {
        this.$message.error('上传头像图片只能是 JPG 或 PNG 格式!')
      }
      if (!isLt2M) {
        this.$message.error('上传头像图片大小不能超过 2MB!')
      }
      return isJPG && isLt2M
    },
    uploadAvatar(options) {
      // 模拟上传
      const file = options.file
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => {
        this.form.avatar = reader.result
      }
    },
    submitForm() {
      this.$refs.form.validate(valid => {
        if (valid) {
          if (this.isEdit) {
            // 模拟更新操作
            const index = this.mockData.findIndex(item => item.id === this.form.id)
            if (index !== -1) {
              this.mockData[index] = { ...this.form }
              this.$message.success('更新成功')
              this.goBack()
            }
          } else {
            // 模拟创建操作
            const newAccount = {
              ...this.form,
              id: this.mockData.length + 1,
              created_at: new Date().toLocaleString()
            }
            this.mockData.push(newAccount)
            this.$message.success('创建成功')
            this.goBack()
          }
        } else {
          return false
        }
      })
    },
    goBack() {
      this.$router.push('/runway/accounts')
    }
  }
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 178px;
  height: 178px;
}

.avatar-uploader:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
}

.avatar-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
</style> 